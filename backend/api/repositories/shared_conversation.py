from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from api.core.models import SharedConversation


class SharedConversationRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
            self,
            conversation_id: int,
            user_id: Optional[int] = None,
            column: Optional[int] = None
    ) -> SharedConversation:
        shared_conv = SharedConversation(
            conversation_id=conversation_id,
            user_id=user_id,
            Column=column,
            created_at=datetime.now(),
            status=1
        )
        self.db.add(shared_conv)
        self.db.commit()
        self.db.refresh(shared_conv)
        return shared_conv
    
    def get_by_id(self, id: int) -> Optional[SharedConversation]:
        return self.db.query(SharedConversation).filter(
            and_(
                SharedConversation.id == id,
                SharedConversation.status == 1
            )
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[SharedConversation]:
        return self.db.query(SharedConversation).filter(
            SharedConversation.status == 1
        ).offset(skip).limit(limit).all()
    
    def get_by_conversation_id(self, conversation_id: int) -> List[SharedConversation]:
        return self.db.query(SharedConversation).filter(
            and_(
                SharedConversation.conversation_id == conversation_id,
                SharedConversation.status == 1
            )
        ).all()
    
    def get_by_user_id(self, user_id: int) -> List[SharedConversation]:
        return self.db.query(SharedConversation).filter(
            and_(
                SharedConversation.user_id == user_id,
                SharedConversation.status == 1
            )
        ).all()
    
    def update(self, id: int, **kwargs) -> Optional[SharedConversation]:
        shared_conv = self.get_by_id(id)
        if not shared_conv:
            return None
        
        for key, value in kwargs.items():
            if hasattr(shared_conv, key):
                setattr(shared_conv, key, value)
        
        shared_conv.last_updated = datetime.now()
        self.db.commit()
        self.db.refresh(shared_conv)
        return shared_conv
    
    def delete(self, id: int) -> bool:
        shared_conv = self.get_by_id(id)
        if not shared_conv:
            return False
        
        shared_conv.status = 0
        shared_conv.last_updated = datetime.now()
        self.db.commit()
        return True
    
    def delete_by_conversation_id(self, conversation_id: int) -> bool:
        shared_convs = self.get_by_conversation_id(conversation_id)
        if not shared_convs:
            return False
        
        for shared_conv in shared_convs:
            shared_conv.status = 0
            shared_conv.last_updated = datetime.now()
        
        self.db.commit()
        return True