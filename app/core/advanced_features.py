# app/core/advanced_features.py
import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

# --- Enhanced Logging Setup ---
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m', 'INFO': '\033[32m', 'WARNING': '\033[33m',
        'ERROR': '\033[31m', 'CRITICAL': '\033[35m', 'RESET': '\033[0m'
    }
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        return super().format(record)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Class Definitions ---

class ConversationPhase(Enum):
    GREETING = "greeting"
    INFORMATION_GATHERING = "info_gathering"
    PROBLEM_SOLVING = "problem_solving"
    CASUAL_CHAT = "casual_chat"
    WRAP_UP = "wrap_up"
    ARCHIVED = "archived"

class CacheManager:
    """Simple memory-based caching system."""
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    async def get(self, key: str) -> Optional[Any]:
        try:
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if item['expires'] > time.time():
                    self.cache_hits += 1
                    return item['value']
                else:
                    del self.memory_cache[key]
            self.cache_misses += 1
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            self.memory_cache[key] = {'value': value, 'expires': time.time() + ttl}
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'hits': self.cache_hits, 'misses': self.cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache)
        }

class PerformanceMonitor:
    """Simple performance monitoring."""
    def __init__(self, window_size: int = 1000):
        self.response_times = deque(maxlen=window_size)
        self.error_count = 0
        self.total_requests = 0
        self.concurrent_requests = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    @asynccontextmanager
    async def measure_request(self):
        start_time = time.time()
        with self.lock:
            self.concurrent_requests += 1
            self.total_requests += 1
        try:
            yield
        except Exception:
            with self.lock:
                self.error_count += 1
            raise
        finally:
            duration = time.time() - start_time
            with self.lock:
                self.response_times.append(duration)
                self.concurrent_requests -= 1

    def get_metrics(self) -> Dict[str, Any]:
        with self.lock:
            response_times_list = list(self.response_times)
        uptime = time.time() - self.start_time
        metrics = {
            'uptime_seconds': round(uptime, 2),
            'total_requests': self.total_requests,
            'error_count': self.error_count,
            'error_rate_percent': round((self.error_count / max(self.total_requests, 1)) * 100, 2),
            'concurrent_requests': self.concurrent_requests,
        }
        if response_times_list:
            avg_time = sum(response_times_list) / len(response_times_list)
            sorted_times = sorted(response_times_list)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if sorted_times else 0
            
            metrics.update({
                'avg_response_time_ms': round(avg_time * 1000, 2),
                'p95_response_time_ms': round(p95_time * 1000, 2),
            })
        return metrics

class ConversationStateManager:
    def __init__(self):
        self.conversation_states = {}
        
    def analyze_conversation_phase(self, messages: List[Any]) -> ConversationPhase:
        if not messages: 
            return ConversationPhase.GREETING
        message_content = " ".join([msg.content for msg in messages[-5:]])
        content_lower = message_content.lower()
        if any(kw in content_lower for kw in ['help', 'problem', 'issue']): 
            return ConversationPhase.PROBLEM_SOLVING
        if any(kw in content_lower for kw in ['hello', 'hi', 'hey']) and len(messages) <= 2: 
            return ConversationPhase.GREETING
        return ConversationPhase.INFORMATION_GATHERING
        
    def update_conversation_state(self, conversation_id: str, messages: List[Any]) -> Dict[str, Any]:
        current_phase = self.analyze_conversation_phase(messages)
        self.conversation_states[conversation_id] = {'phase': current_phase}
        return self.conversation_states[conversation_id]
        
    def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        return self.conversation_states.get(conversation_id, {'error': 'State not found'})

class PersonaConsistencyChecker:
    def __init__(self):
        pass
        
    def analyze_persona_consistency(self, persona_content: str, responses: List[str]) -> Dict[str, Any]:
        # Simple consistency check without sklearn
        if not responses: 
            return {'consistency_score': 1.0}
        try:
            # Basic keyword matching approach
            persona_words = set(persona_content.lower().split())
            response_words = set()
            for response in responses:
                response_words.update(response.lower().split())
            
            common_words = persona_words.intersection(response_words)
            score = len(common_words) / max(len(persona_words), 1)
            return {'consistency_score': round(min(score, 1.0), 3)}
        except Exception as e:
            logger.error(f"Persona consistency analysis error: {e}")
            return {'consistency_score': 0.0, 'error': str(e)}

class ConversationArchiver:
    """Handles conversation archival and cleanup."""
    async def cleanup_old_conversations(self, db: Session, max_age_days: int = 7) -> Dict[str, Any]:
        logger.info("Executing database cleanup/archival task...")
        return {'cleaned_conversations': 0, 'status': 'Placeholder execution.'}

class EnhancedMessageProcessor:
    """Enhanced message processor with advanced features."""
    def __init__(self, llm_provider, persona_manager, context_manager, cache_manager, performance_monitor):
        self.llm_provider = llm_provider
        self.persona_manager = persona_manager
        self.context_manager = context_manager
        self.cache_manager = cache_manager
        self.performance_monitor = performance_monitor
        self.state_manager = ConversationStateManager()
        self.consistency_checker = PersonaConsistencyChecker()
        self.archiver = ConversationArchiver()

    def create_messages_hash(self, messages: List[Dict]) -> str:
        messages_str = json.dumps(messages, sort_keys=True)
        return hashlib.md5(messages_str.encode()).hexdigest()

    async def generate_cached_response(self, messages_hash: str, messages: List[Dict]) -> Optional[str]:
        cached_response = await self.cache_manager.get(f"response:{messages_hash}")
        if cached_response:
            return cached_response
        response = await self.llm_provider.generate_response(messages)
        await self.cache_manager.set(f"response:{messages_hash}", response, ttl=1800)
        return response

    def generate_state_aware_prompt(self, conversation_state: Dict[str, Any], summary: Optional[str] = None) -> str:
        base_prompt = self.persona_manager.generate_system_prompt(summary=summary)
        phase = conversation_state.get('phase', ConversationPhase.INFORMATION_GATHERING)
        return f"{base_prompt}\n\nCONVERSATION CONTEXT:\nCurrent Phase: {phase.value}"

    async def process_message_enhanced(self, db_session: Session, conversation_id: str, user_input: str) -> Dict[str, Any]:
        """Main processing pipeline with database integration."""
        async with self.performance_monitor.measure_request():
            try:
                start_time = time.time()
                from app.core.chatbot_core import Message, ConversationSummary

                user_message = Message(role='user', content=user_input)
                self.context_manager.add_message(db_session, conversation_id, user_message)

                messages = self.context_manager.get_conversation_history(db_session, conversation_id)
                conversation_state = self.state_manager.update_conversation_state(conversation_id, messages)

                summary_created = False
                if self.context_manager.should_summarize(db_session, conversation_id):
                    messages_to_summarize = self.context_manager.get_messages_for_summarization(db_session, conversation_id)
                    if messages_to_summarize:
                        summary_text = "Summary of previous messages."
                        summary = ConversationSummary(summary_text=summary_text, message_range=(0,0))
                        self.context_manager.add_summary(db_session, conversation_id, summary)
                        summary_created = True

                message_history, latest_summary = self.context_manager.prepare_context_for_llm(db_session, conversation_id, self.llm_provider)
                system_prompt = self.generate_state_aware_prompt(conversation_state, latest_summary)
                llm_messages = [{'role': 'system', 'content': system_prompt}] + message_history

                messages_hash = self.create_messages_hash(llm_messages)
                response = await self.generate_cached_response(messages_hash, llm_messages)

                assistant_message = Message(role='assistant', content=response)
                self.context_manager.add_message(db_session, conversation_id, assistant_message)

                final_message_count = len(messages) + 1
                processing_time = (time.time() - start_time) * 1000

                return {
                    'success': True, 'response': response, 'conversation_id': conversation_id,
                    'message_count': final_message_count, 'summary_created': summary_created,
                    'processing_time_ms': round(processing_time, 2),
                    'conversation_state': {'current_phase': conversation_state['phase'].value},
                    'cache_stats': self.cache_manager.get_stats()
                }
            except Exception as e:
                logger.error(f"Enhanced message processing error: {e}", exc_info=True)
                return {'success': False, 'error': str(e), 'conversation_id': conversation_id}

class HealthChecker:
    """Comprehensive health checking system."""
    def __init__(self, engine):
        self.engine = engine
        
    async def run_comprehensive_health_check(self, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        health_status = {'timestamp': datetime.now().isoformat(), 'overall_status': 'healthy', 'components': {}, 'issues': []}
        try:
            await self.engine.llm_provider.generate_response([{'role': 'user', 'content': 'Health check'}], max_tokens=5)
            health_status['components']['llm_provider'] = {'status': 'healthy'}
        except Exception as e:
            health_status['components']['llm_provider'] = {'status': 'error', 'error': str(e)}
            health_status['issues'].append("LLM Provider Error")
        
        health_status['metrics'] = self.engine.get_system_metrics(db)
        if health_status['issues']: 
            health_status['overall_status'] = 'unhealthy'
        health_status['check_duration_ms'] = round((time.time() - start_time) * 1000, 2)
        return health_status

class EnhancedChatbotEngine:
    """Enhanced chatbot engine integrating all features."""
    def __init__(self, openai_api_key: str, persona_file_path: str, redis_url: Optional[str] = None):
        from app.core.chatbot_core import OpenAIProvider, PersonaManager, ContextManager
        self.llm_provider = OpenAIProvider(openai_api_key)
        self.persona_manager = PersonaManager(persona_file_path)
        self.context_manager = ContextManager()
        self.cache_manager = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        self.message_processor = EnhancedMessageProcessor(
            self.llm_provider, self.persona_manager, self.context_manager,
            self.cache_manager, self.performance_monitor
        )
        logger.info("Enhanced Chatbot Engine initialized")

    async def chat_enhanced(self, db_session: Session, conversation_id: str, user_input: str) -> Dict[str, Any]:
        return await self.message_processor.process_message_enhanced(db_session, conversation_id, user_input)

    def get_system_metrics(self, db: Session) -> Dict[str, Any]:
        from app.db import models
        active_count = db.query(models.Conversation).count()
        total_messages = db.query(models.Message).count()
        return {
            'performance': self.performance_monitor.get_metrics(),
            'cache': self.cache_manager.get_stats(),
            'conversations': {'active_count': active_count, 'total_messages': total_messages}
        }

    async def run_maintenance(self, db: Session) -> Dict[str, Any]:
        logger.info("Running system maintenance...")
        cleanup_result = await self.message_processor.archiver.cleanup_old_conversations(db)
        return {'timestamp': datetime.now().isoformat(), 'cleanup_result': cleanup_result}

class ProductionChatbotEngine(EnhancedChatbotEngine):
    """Production-ready engine with background tasks."""
    def __init__(self, openai_api_key: str, persona_file_path: str, redis_url: Optional[str] = None):
        super().__init__(openai_api_key, persona_file_path, redis_url)
        self.health_checker = HealthChecker(self)
        self.background_tasks_running = True
        self.background_tasks = []
        logger.info("Production Chatbot Engine initialized with all features")

    async def get_comprehensive_status(self) -> Dict[str, Any]:
        from app.db.database import SessionLocal
        with SessionLocal() as db:
            health_status = await self.health_checker.run_comprehensive_health_check(db)
            system_metrics = self.get_system_metrics(db)
        return {
            'timestamp': datetime.now().isoformat(),
            'health': health_status,
            'system_metrics': system_metrics,
            'background_tasks_status': {
                'running': self.background_tasks_running,
                'task_count': len(self.background_tasks)
            }
        }

    async def shutdown(self):
        logger.info("Shutting down Production Chatbot Engine...")
        self.background_tasks_running = False
        for task in self.background_tasks:
            task.cancel()
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("Production Chatbot Engine shutdown complete.")