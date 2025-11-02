from typing import Optional, List
import datetime
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, REAL, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .db import Base


class Prompt(Base):
    __tablename__ = 'prompt'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='prompt_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    agent: Mapped[list['Agent']] = relationship('Agent', back_populates='prompt')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='role_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped[list['User']] = relationship('User', back_populates='role')


class Agent(Base):
    __tablename__ = 'agent'
    __table_args__ = (
        ForeignKeyConstraint(['prompt_id'], ['prompt.id'], name='fkagent352251'),
        PrimaryKeyConstraint('id', name='agent_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_id: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    prompt: Mapped['Prompt'] = relationship('Prompt', back_populates='agent')
    conversation_agent: Mapped[list['ConversationAgent']] = relationship('ConversationAgent', back_populates='agent')
    message: Mapped[list['Message']] = relationship('Message', back_populates='agent')


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['role.id'], name='fkuser994439'),
        PrimaryKeyConstraint('id', name='user_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    role: Mapped['Role'] = relationship('Role', back_populates='user')
    conversation: Mapped[list['Conversation']] = relationship('Conversation', back_populates='user')
    message: Mapped[list['Message']] = relationship('Message', back_populates='user')


class Conversation(Base):
    __tablename__ = 'conversation'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='fkconversati624844'),
        PrimaryKeyConstraint('id', name='conversation_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False)
    share_token: Mapped[str] = mapped_column(String(255), nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    summary: Mapped[Optional[str]] = mapped_column(String(255))
    summary_embedding: Mapped[Optional[List[float]]] = mapped_column(PG_ARRAY(Float))

    user: Mapped['User'] = relationship('User', back_populates='conversation')
    conversation_agent: Mapped[list['ConversationAgent']] = relationship('ConversationAgent', back_populates='conversation')
    shared_conversation: Mapped[list['SharedConversation']] = relationship('SharedConversation', back_populates='conversation')
    message: Mapped[list['Message']] = relationship('Message', back_populates='conversation')


class ConversationAgent(Base):
    __tablename__ = 'conversation_agent'
    __table_args__ = (
        ForeignKeyConstraint(['agent_id'], ['agent.id'], name='fkconversati968934'),
        ForeignKeyConstraint(['conversation_id'], ['conversation.id'], name='fkconversati48128'),
        PrimaryKeyConstraint('id', name='conversation_agent_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    agent: Mapped['Agent'] = relationship('Agent', back_populates='conversation_agent')
    conversation: Mapped['Conversation'] = relationship('Conversation', back_populates='conversation_agent')


class SharedConversation(Base):
    __tablename__ = 'shared_conversation'
    __table_args__ = (
        ForeignKeyConstraint(['conversation_id'], ['conversation.id'], name='fkshared_con465607'),
        PrimaryKeyConstraint('id', name='shared_conversation_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    Column: Mapped[Optional[int]] = mapped_column(Integer)

    conversation: Mapped['Conversation'] = relationship('Conversation', back_populates='shared_conversation')
    message: Mapped[list['Message']] = relationship('Message', back_populates='shared_conversation')


class Message(Base):
    __tablename__ = 'message'
    __table_args__ = (
        ForeignKeyConstraint(['agent_id'], ['agent.id'], name='fkmessage131510'),
        ForeignKeyConstraint(['conversation_id'], ['conversation.id'], name='fkmessage760887'),
        ForeignKeyConstraint(['shared_conversation_id'], ['shared_conversation.id'], name='fkmessage722037'),
        ForeignKeyConstraint(['user_id'], ['user.id'], name='fkmessage395623'),
        PrimaryKeyConstraint('id', name='message_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[int] = mapped_column(Integer, nullable=False)
    message_type: Mapped[int] = mapped_column(Integer, nullable=False)
    shared_conversation_id: Mapped[Optional[int]] = mapped_column(Integer)
    conversation_id: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, comment='user id hoặc agent id')
    agent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='user id hoặc agent id')
    reaction: Mapped[Optional[str]] = mapped_column(String(255))
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    agent: Mapped[Optional['Agent']] = relationship('Agent', back_populates='message')
    conversation: Mapped[Optional['Conversation']] = relationship('Conversation', back_populates='message')
    shared_conversation: Mapped[Optional['SharedConversation']] = relationship('SharedConversation', back_populates='message')
    user: Mapped[Optional['User']] = relationship('User', back_populates='message')