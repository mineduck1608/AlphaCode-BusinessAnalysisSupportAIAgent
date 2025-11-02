"""Pydantic schemas for API request/response models."""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


# ----------------- Base Schemas -----------------
class PromptBase(BaseModel):
    name: str
    content: str


class PromptCreate(PromptBase):
    pass


class Prompt(PromptBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True  # orm_mode is deprecated in Pydantic v2


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentBase(BaseModel):
    name: str
    provider: str
    model: str
    avatar_url: str
    prompt_id: int


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    role_id: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    name: str
    user_id: int


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    status: int
    is_shared: bool = False
    session: Optional[str] = None
    last_updated: Optional[datetime] = None
    summary: Optional[str] = None
    summary_embedding: Optional[List[float]] = None

    class Config:
        from_attributes = True


class ConversationAgentBase(BaseModel):
    conversation_id: int
    agent_id: int
    is_active: bool = True


class ConversationAgentCreate(ConversationAgentBase):
    pass


class ConversationAgent(ConversationAgentBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class SharedConversationBase(BaseModel):
    conversation_id: int


class SharedConversationCreate(SharedConversationBase):
    pass


class SharedConversation(SharedConversationBase):
    id: int
    created_at: datetime
    status: int
    last_updated: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    role: int
    content: str
    content_type: int
    message_type: int


class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None
    shared_conversation_id: Optional[int] = None
    user_id: Optional[int] = None
    agent_id: Optional[int] = None


class Message(MessageBase):
    id: int
    created_at: datetime
    status: int
    shared_conversation_id: Optional[int] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    reaction: Optional[str] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True
