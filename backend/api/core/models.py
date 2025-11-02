from typing import List, Optional
from pydantic import BaseModel
import datetime

# ----------------- Base Schemas -----------------
class Prompt(BaseModel):
    id: int
    name: str
    content: str
    created_at: datetime.datetime
    status: int
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class Role(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    status: int
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class Agent(BaseModel):
    id: int
    name: str
    provider: str
    model: str
    avatar_url: str
    created_at: datetime.datetime
    status: int
    prompt_id: int
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    email: str
    role_id: int
    created_at: datetime.datetime
    status: int
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class Conversation(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime.datetime
    status: int
    is_shared: bool
    share_token: str
    last_updated: Optional[datetime.datetime]
    summary: Optional[str]
    summary_embedding: Optional[List[float]]

    class Config:
        orm_mode = True


class ConversationAgent(BaseModel):
    id: int
    conversation_id: int
    agent_id: int
    is_active: bool
    created_at: datetime.datetime
    status: int
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class SharedConversation(BaseModel):
    id: int
    conversation_id: int
    created_at: datetime.datetime
    status: int
    last_updated: Optional[datetime.datetime]
    user_id: Optional[int]
    Column: Optional[int]

    class Config:
        orm_mode = True


class Message(BaseModel):
    id: int
    role: int
    created_at: datetime.datetime
    status: int
    content: str
    content_type: int
    message_type: int
    shared_conversation_id: Optional[int]
    conversation_id: Optional[int]
    user_id: Optional[int]
    agent_id: Optional[int]
    reaction: Optional[str]
    last_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True
