from typing import List, Optional
from sqlalchemy.orm import Session

from api.repositories.shared_conversation import SharedConversationRepository
from api.core.models import SharedConversation
from services.mcp_vector.src.models.db import session

from typing import List, Optional

class SharedConversationService:
    
    def __init__(self):
        self.db = session
        self.repository = SharedConversationRepository(self.db)
    
    def create_shared_conversation(
            self,
            conversation_id: int,
            user_id: Optional[int] = None,
            column: Optional[int] = None
    ) -> SharedConversation:
        return self.repository.create(
            conversation_id=conversation_id,
            user_id=user_id,
            column=column
        )
    
    def get_shared_conversation(self, id: int) -> Optional[SharedConversation]:
        return self.repository.get_by_id(id)
    
    def get_all_shared_conversations(self, skip: int = 0, limit: int = 100) -> List[SharedConversation]:
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_shared_conversations_by_conversation(self, conversation_id: int) -> List[SharedConversation]:
        return self.repository.get_by_conversation_id(conversation_id)
    
    def get_shared_conversations_by_user(self, user_id: int) -> List[SharedConversation]:
        return self.repository.get_by_user_id(user_id)
    
    def update_shared_conversation(self, id: int, **kwargs) -> Optional[SharedConversation]:
        return self.repository.update(id, **kwargs)
    
    def delete_shared_conversation(self, id: int) -> bool:
        return self.repository.delete(id)
    
    def delete_shared_conversations_by_conversation(self, conversation_id: int) -> bool:
        return self.repository.delete_by_conversation_id(conversation_id)
    
    def share_conversation_to_user(
            self,
            conversation_id: int,
            target_user_id: int
    ) -> Optional[SharedConversation]:
        existing = self.repository.get_by_conversation_id(conversation_id)
        for shared_conv in existing:
            if shared_conv.user_id == target_user_id:
                return shared_conv
        
        return self.repository.create(
            conversation_id=conversation_id,
            user_id=target_user_id
        )