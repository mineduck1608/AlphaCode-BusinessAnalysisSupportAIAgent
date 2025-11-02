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


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


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


class RoleUpdate(BaseModel):
    name: Optional[str] = None


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


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    avatar_url: Optional[str] = None
    prompt_id: Optional[int] = None
    status: Optional[int] = None


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
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None


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
    is_shared: bool = False
    summary: Optional[str] = None


class ConversationUpdate(BaseModel):
    name: Optional[str] = None
    is_shared: Optional[bool] = None
    summary: Optional[str] = None


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


class ConversationAgentUpdate(BaseModel):
    is_active: Optional[bool] = None


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
    user_id: Optional[int] = None
    column: Optional[int] = None


class SharedConversationUpdate(BaseModel):
    user_id: Optional[int] = None
    column: Optional[int] = None


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
    reaction: Optional[str] = None


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    reaction: Optional[str] = None
    content_type: Optional[int] = None
    message_type: Optional[int] = None


class MessageReactionUpdate(BaseModel):
    reaction: str


class UserMessageCreate(BaseModel):
    content: str
    user_id: int
    conversation_id: int
    content_type: int = 1
    message_type: int = 1


class AgentMessageCreate(BaseModel):
    content: str
    agent_id: int
    conversation_id: int
    content_type: int = 1
    message_type: int = 1


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