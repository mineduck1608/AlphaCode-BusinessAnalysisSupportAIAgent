"""SQLAlchemy ORM models for database tables."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    last_updated = Column(DateTime, nullable=True)


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    last_updated = Column(DateTime, nullable=True)


class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    avatar_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    prompt_id = Column(Integer, ForeignKey("prompt.id"))
    last_updated = Column(DateTime, nullable=True)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    last_updated = Column(DateTime, nullable=True)


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    is_shared = Column(Boolean, default=False)
    session = Column(String, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    summary_embedding = Column(ARRAY(Float), nullable=True)


class ConversationAgent(Base):
    __tablename__ = "conversation_agent"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    agent_id = Column(Integer, ForeignKey("agent.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    last_updated = Column(DateTime, nullable=True)


class SharedConversation(Base):
    __tablename__ = "shared_conversation"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    last_updated = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    content_type = Column(Integer, nullable=False)
    message_type = Column(Integer, nullable=False)
    shared_conversation_id = Column(Integer, ForeignKey("shared_conversation.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=True)
    reaction = Column(String, nullable=True)
    last_updated = Column(DateTime, nullable=True)
