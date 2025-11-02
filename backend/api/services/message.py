from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from api.repositories.message import MessageRepository
from api.core.models import Message
from services.mcp_vector.src.models.db import session


class MessageService:
    
    def __init__(self):
        self.db = session
        self.repository = MessageRepository(self.db)
    
    def create_message(
            self,
            role: int,
            content: str,
            content_type: int,
            message_type: int,
            conversation_id: Optional[int] = None,
            shared_conversation_id: Optional[int] = None,
            user_id: Optional[int] = None,
            agent_id: Optional[int] = None,
            reaction: Optional[str] = None
    ) -> Message:
        return self.repository.create(
            role=role,
            content=content,
            content_type=content_type,
            message_type=message_type,
            conversation_id=conversation_id,
            shared_conversation_id=shared_conversation_id,
            user_id=user_id,
            agent_id=agent_id,
            reaction=reaction
        )
    
    def get_message(self, id: int) -> Optional[Message]:
        return self.repository.get_by_id(id)
    
    def get_all_messages(self, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_conversation_messages(
            self,
            conversation_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Message]:
        return self.repository.get_by_conversation_id(
            conversation_id,
            skip=skip,
            limit=limit
        )
    
    def get_shared_conversation_messages(
            self,
            shared_conversation_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Message]:
        return self.repository.get_by_shared_conversation_id(
            shared_conversation_id,
            skip=skip,
            limit=limit
        )
    
    def get_user_messages(self, user_id: int) -> List[Message]:
        return self.repository.get_by_user_id(user_id)
    
    def get_agent_messages(self, agent_id: int) -> List[Message]:
        return self.repository.get_by_agent_id(agent_id)
    
    def update_message(self, id: int, **kwargs) -> Optional[Message]:
        return self.repository.update(id, **kwargs)
    
    def update_message_reaction(self, id: int, reaction: str) -> Optional[Message]:
        return self.repository.update_reaction(id, reaction)
    
    def delete_message(self, id: int) -> bool:
        return self.repository.delete(id)
    
    def delete_conversation_messages(self, conversation_id: int) -> bool:
        return self.repository.delete_by_conversation_id(conversation_id)
    
    def delete_shared_conversation_messages(self, shared_conversation_id: int) -> bool:
        return self.repository.delete_by_shared_conversation_id(shared_conversation_id)
    
    def get_conversation_with_relations(self, conversation_id: int) -> List[Message]:
        return self.repository.get_with_relations(conversation_id)
    
    def get_conversation_statistics(self, conversation_id: int) -> Dict[str, Any]:
        return self.repository.get_conversation_statistics(conversation_id)
    
    def create_user_message(
            self,
            content: str,
            user_id: int,
            conversation_id: int,
            content_type: int = 1,
            message_type: int = 1
    ) -> Message:
        return self.create_message(
            role=1,
            content=content,
            content_type=content_type,
            message_type=message_type,
            conversation_id=conversation_id,
            user_id=user_id
        )
    
    def create_agent_message(
            self,
            content: str,
            agent_id: int,
            conversation_id: int,
            content_type: int = 1,
            message_type: int = 1
    ) -> Message:
        return self.create_message(
            role=2,
            content=content,
            content_type=content_type,
            message_type=message_type,
            conversation_id=conversation_id,
            agent_id=agent_id
        )