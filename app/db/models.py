# app/db/models.py
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  
    user_id = Column(String, index=True, nullable=False)  
    title = Column(Text, default="New Conversation")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)  
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)  
    role = Column(Text, nullable=False)  # 'user', 'assistant', or 'system'
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True, autoincrement=True)  
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)  
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="summaries")