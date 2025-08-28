import os
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import openai
from openai import OpenAI
import asyncio
import aiohttp
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class ConversationSummary:
    """Represents a conversation summary"""
    summary_text: str
    message_range: Tuple[int, int]  # (start_index, end_index)
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class LLMProvider:
    """Base class for LLM providers"""
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    async def generate_response(self, messages: List[Dict]) -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    def __init__(self, api_key: str, model: str = "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"): 
        super().__init__(api_key, model)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1" 
        )

    async def generate_response(self, messages: List[Dict], max_tokens: int = 1000) -> str:
        """Generate response using OpenAI API with simple retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    extra_headers={ 
                        "HTTP-Referer": "http://localhost", 
                        "X-Title": "DaddyJohn AI Chatbot" 
                    }
                )
                return response.choices[0].message.content
            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise
            except openai.APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
    
    def count_tokens(self, text: str) -> int:
        """Simple token estimation: ~4 characters per token"""
        return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """Count total tokens in messages"""
        total = 0
        for message in messages:
            total += self.count_tokens(message['content'])
            total += 4  # Every message has overhead tokens
        return total

class PersonaManager:
    """Manages persona loading and system prompt generation"""
    
    def __init__(self, persona_file_path: str = "persona.txt"):
        self.persona_file_path = persona_file_path
        self.persona_content = ""
        self.load_persona()
    
    def load_persona(self) -> None:
        """Load persona from file"""
        try:
            if os.path.exists(self.persona_file_path):
                with open(self.persona_file_path, 'r', encoding='utf-8') as f:
                    self.persona_content = f.read().strip()
                logger.info("Persona loaded successfully")
            else:
                logger.warning(f"Persona file not found: {self.persona_file_path}")
                self.persona_content = "You are a helpful and friendly AI assistant."
        except Exception as e:
            logger.error(f"Error loading persona: {e}")
            self.persona_content = "You are a helpful and friendly AI assistant."
    
    def update_persona(self, new_persona: str) -> None:
        """Update persona content"""
        self.persona_content = new_persona
        try:
            with open(self.persona_file_path, 'w', encoding='utf-8') as f:
                f.write(new_persona)
            logger.info("Persona updated successfully")
        except Exception as e:
            logger.error(f"Error saving persona: {e}")
    
    def validate_persona(self) -> bool:
        """Validate persona content"""
        if not self.persona_content or len(self.persona_content.strip()) < 10:
            return False
        return True
    
    def generate_system_prompt(self, context: Optional[str] = None, summary: Optional[str] = None) -> str:
        """Generate system prompt with persona and context"""
        system_prompt = f"PERSONA:\n{self.persona_content}\n\n"
        
        if summary:
            system_prompt += f"CONVERSATION SUMMARY:\n{summary}\n\n"
        
        if context:
            system_prompt += f"CONTEXT:\n{context}\n\n"
        
        system_prompt += "INSTRUCTIONS:\nRespond in character according to the persona above. Maintain consistency with the conversation history and summary if provided."
        
        return system_prompt

class ContextManager:
    """Manages conversation context and message history"""
    
    def __init__(self, max_context_tokens: int = 3000, summarize_threshold: int = 20):
        self.max_context_tokens = max_context_tokens
        self.summarize_threshold = summarize_threshold
    
    def add_message(self, db: Session, conversation_id: str, message: Message) -> None:
        """Saves a message to the database."""
        from app.db import crud
        crud.create_message(db=db, conversation_id=conversation_id, message=message)

    def get_conversation_history(self, db: Session, conversation_id: str) -> List[Message]:
        """Gets full conversation history from the database."""
        from app.db import crud
        db_messages = crud.get_conversation_messages(db=db, conversation_id=conversation_id)
        return [Message(role=msg.role, content=msg.content, timestamp=msg.created_at) for msg in db_messages]

    def should_summarize(self, db: Session, conversation_id: str) -> bool:
        """Checks if conversation should be summarized based on DB count."""
        from app.db import crud
        count = crud.get_user_assistant_message_count(db=db, conversation_id=conversation_id)
        return count > 0 and count % self.summarize_threshold == 0

    def get_messages_for_summarization(self, db: Session, conversation_id: str) -> List[Message]:
        """Gets the last messages for summarization from the database."""
        history = self.get_conversation_history(db=db, conversation_id=conversation_id)
        user_assistant_messages = [m for m in history if m.role in ['user', 'assistant']]
        return user_assistant_messages[-self.summarize_threshold:]

    def add_summary(self, db: Session, conversation_id: str, summary: ConversationSummary) -> None:
        """Saves a summary to the database."""
        from app.db import crud
        crud.create_summary(db=db, conversation_id=conversation_id, summary=summary)

    def get_latest_summary(self, db: Session, conversation_id: str) -> Optional[str]:
        """Gets the most recent summary from the database."""
        from app.db import crud
        latest_summary = crud.get_latest_summary(db=db, conversation_id=conversation_id)
        return latest_summary.summary_text if latest_summary else None

    def prepare_context_for_llm(self, db: Session, conversation_id: str, llm_provider: 'LLMProvider') -> Tuple[List[Dict], Optional[str]]:
        """Prepares context for the LLM using data from the database."""
        messages = self.get_conversation_history(db=db, conversation_id=conversation_id)
        summary = self.get_latest_summary(db=db, conversation_id=conversation_id)

        message_dicts = [{'role': msg.role, 'content': msg.content} for msg in messages if msg.role != 'system']

        if hasattr(llm_provider, 'count_messages_tokens'):
            while message_dicts and llm_provider.count_messages_tokens(message_dicts) > self.max_context_tokens:
                message_dicts.pop(0)

        return message_dicts, summary

class MessageProcessor:
    """Handles the complete message processing pipeline"""
    
    def __init__(self, llm_provider: LLMProvider, persona_manager: PersonaManager, context_manager: ContextManager):
        self.llm_provider = llm_provider
        self.persona_manager = persona_manager
        self.context_manager = context_manager
    
    def validate_input(self, user_input: str) -> bool:
        """Validate user input"""
        if not user_input or not user_input.strip():
            return False
        if len(user_input) > 2000:  # Max input length
            return False
        return True
    
    async def generate_summary(self, messages: List[Message]) -> str:
        """Generate summary of conversation messages"""
        if not messages:
            return "No messages to summarize."
        
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in messages
        ])
        
        summary_prompt = f"""Please provide a concise summary of this conversation that captures:
1. Key topics discussed
2. Important decisions or conclusions
3. User's preferences or specific requests
4. Emotional tone and relationship dynamics

Conversation:
{conversation_text}

Summary:"""
        
        summary_messages = [{'role': 'user', 'content': summary_prompt}]
        return await self.llm_provider.generate_response(summary_messages)
    
    async def process_message(self, db: Session, conversation_id: str, user_input: str) -> Dict:
        """Main message processing pipeline"""
        try:
            if not self.validate_input(user_input):
                return {
                    'success': False,
                    'error': 'Invalid input: message is empty or too long',
                    'response': None
                }
            
            user_message = Message(role='user', content=user_input)
            self.context_manager.add_message(db, conversation_id, user_message)
            
            if self.context_manager.should_summarize(db, conversation_id):
                messages_to_summarize = self.context_manager.get_messages_for_summarization(db, conversation_id)
                if messages_to_summarize:
                    summary_text = await self.generate_summary(messages_to_summarize)
                    summary = ConversationSummary(
                        summary_text=summary_text,
                        message_range=(0, len(messages_to_summarize))
                    )
                    self.context_manager.add_summary(db, conversation_id, summary)
                    logger.info(f"Created summary for conversation {conversation_id}")
            
            message_history, latest_summary = self.context_manager.prepare_context_for_llm(
                db, conversation_id, self.llm_provider
            )
            
            system_prompt = self.persona_manager.generate_system_prompt(
                summary=latest_summary
            )
            
            llm_messages = [{'role': 'system', 'content': system_prompt}]
            llm_messages.extend(message_history)
            
            response = await self.llm_provider.generate_response(llm_messages)
            
            assistant_message = Message(role='assistant', content=response)
            self.context_manager.add_message(db, conversation_id, assistant_message)
            
            return {
                'success': True,
                'response': response,
                'summary_created': False,
                'message_count': len(self.context_manager.get_conversation_history(db, conversation_id)),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }

class ChatbotEngine:
    """Main chatbot engine that orchestrates all components"""
    
    def __init__(self, openai_api_key: str, persona_file_path: str = "persona.txt"):
        self.llm_provider = OpenAIProvider(openai_api_key)
        self.persona_manager = PersonaManager(persona_file_path)
        self.context_manager = ContextManager()
        self.message_processor = MessageProcessor(
            self.llm_provider,
            self.persona_manager,
            self.context_manager
        )
        
        logger.info("Chatbot engine initialized successfully")
    
    async def chat(self, db: Session, conversation_id: str, user_input: str) -> Dict:
        """Main chat interface with database session"""
        return await self.message_processor.process_message(db, conversation_id, user_input)
    
    def create_conversation(self, conversation_id: str) -> Dict:
        """Create a new conversation"""
        return {
            'success': True,
            'conversation_id': conversation_id
        }
    
    def get_conversation_history(self, db: Session, conversation_id: str) -> Dict:
        """Get conversation history with database session"""
        history = self.context_manager.get_conversation_history(db, conversation_id)
        return {
            'success': True,
            'history': [msg.to_dict() for msg in history],
            'message_count': len(history)
        }
    
    def update_persona(self, new_persona: str) -> Dict:
        """Update the persona"""
        try:
            self.persona_manager.update_persona(new_persona)
            return {
                'success': True,
                'message': 'Persona updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_conversation_summaries(self, db: Session, conversation_id: str) -> Dict:
        """Get all summaries for a conversation with database session"""
        summaries = self.context_manager.get_latest_summary(db, conversation_id)
        return {
            'success': True,
            'summaries': [
                {
                    'summary': summaries,
                    'message_range': None,
                    'created_at': None
                }
            ]
        }

async def example_usage():
    """Example of how to use the chatbot engine"""
    
    engine = ChatbotEngine("your-openai-api-key-here")
    
    print("Chatbot Engine Structure:")
    print("1. Initialize with: engine = ChatbotEngine('your-openai-api-key')")
    print("2. Create conversation: engine.create_conversation('user_123')")
    print("3. Chat: await engine.chat('user_123', 'Hello!')")
    print("4. Update persona: engine.update_persona('New persona content')")
    
    conversation_id = "user_123"
    
    result = engine.create_conversation(conversation_id)
    print(f"Conversation created: {result}")
    
    for i in range(25):  
        response = await engine.chat(conversation_id, user_input=f"This is message {i+1}")
        print(f"Response {i+1}: {response}")
        
    history = engine.get_conversation_history(conversation_id)
    print(f"History: {history}")
    
    summaries = engine.get_conversation_summaries(conversation_id)
    print(f"Summaries: {summaries}")

if __name__ == "__main__":
    asyncio.run(example_usage())