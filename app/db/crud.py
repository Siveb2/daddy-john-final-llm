# app/db/crud.py
from sqlalchemy.orm import Session
from . import models
from app.core.chatbot_core import Message as CoreMessage, ConversationSummary as CoreSummary

## Conversation Functions
def get_or_create_conversation(db: Session, conversation_id: str, user_id: str):
    """
    Retrieves a conversation by its ID or creates it if it doesn't exist.
    This ensures every chat session has a corresponding record in the database.
    """
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conversation:
        db_conversation = models.Conversation(id=conversation_id, user_id=user_id)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: str):
    """Retrieves a single conversation by its ID."""
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def delete_conversation(db: Session, conversation_id: str):
    """Deletes a conversation and its related messages/summaries."""
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation

## Message Functions
def get_conversation_messages(db: Session, conversation_id: str):
    """Retrieves all messages for a given conversation, ordered by creation time."""
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at).all()

def create_message(db: Session, conversation_id: str, message: CoreMessage, token_count: int = 0):
    """Saves a new message to the database."""
    db_message = models.Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        token_count=token_count
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user_assistant_message_count(db: Session, conversation_id: str):
    """Counts only the 'user' and 'assistant' messages for summarization logic."""
    return db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id,
        models.Message.role.in_(['user', 'assistant'])
    ).count()

## Summary Functions
def create_summary(db: Session, conversation_id: str, summary: CoreSummary):
    """Saves a new conversation summary to the database."""
    db_summary = models.Summary(
        conversation_id=conversation_id,
        summary_text=summary.summary_text
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def get_latest_summary(db: Session, conversation_id: str):
    """Retrieves the most recent summary for a conversation."""
    return db.query(models.Summary).filter(models.Summary.conversation_id == conversation_id).order_by(models.Summary.created_at.desc()).first()