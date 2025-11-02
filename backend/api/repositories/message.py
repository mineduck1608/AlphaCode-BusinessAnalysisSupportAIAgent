from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from core.models import Message, User, Agent


class MessageRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
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
        message = Message(
            role=role,
            content=content,
            content_type=content_type,
            message_type=message_type,
            conversation_id=conversation_id,
            shared_conversation_id=shared_conversation_id,
            user_id=user_id,
            agent_id=agent_id,
            reaction=reaction,
            created_at=datetime.now(),
            status=1
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_by_id(self, id: int) -> Optional[Message]:
        return self.db.query(Message).filter(
            and_(
                Message.id == id,
                Message.status == 1
            )
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.db.query(Message).filter(
            Message.status == 1
        ).offset(skip).limit(limit).all()
    
    def get_by_conversation_id(
            self,
            conversation_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Message]:
        return self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.status == 1
            )
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    def get_by_shared_conversation_id(
            self,
            shared_conversation_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Message]:
        return self.db.query(Message).filter(
            and_(
                Message.shared_conversation_id == shared_conversation_id,
                Message.status == 1
            )
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    def get_by_user_id(self, user_id: int) -> List[Message]:
        return self.db.query(Message).filter(
            and_(
                Message.user_id == user_id,
                Message.status == 1
            )
        ).order_by(Message.created_at.asc()).all()
    
    def get_by_agent_id(self, agent_id: int) -> List[Message]:
        return self.db.query(Message).filter(
            and_(
                Message.agent_id == agent_id,
                Message.status == 1
            )
        ).order_by(Message.created_at.asc()).all()
    
    def update(self, id: int, **kwargs) -> Optional[Message]:
        message = self.get_by_id(id)
        if not message:
            return None
        
        for key, value in kwargs.items():
            if hasattr(message, key):
                setattr(message, key, value)
        
        message.last_updated = datetime.now()
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def update_reaction(self, id: int, reaction: str) -> Optional[Message]:
        return self.update(id, reaction=reaction)
    
    def delete(self, id: int) -> bool:
        message = self.get_by_id(id)
        if not message:
            return False
        
        message.status = 0
        message.last_updated = datetime.now()
        self.db.commit()
        return True
    
    def delete_by_conversation_id(self, conversation_id: int) -> bool:
        messages = self.get_by_conversation_id(conversation_id)
        if not messages:
            return False
        
        for message in messages:
            message.status = 0
            message.last_updated = datetime.now()
        
        self.db.commit()
        return True
    
    def delete_by_shared_conversation_id(self, shared_conversation_id: int) -> bool:
        messages = self.get_by_shared_conversation_id(shared_conversation_id)
        if not messages:
            return False
        
        for message in messages:
            message.status = 0
            message.last_updated = datetime.now()
        
        self.db.commit()
        return True
    
    # Advanced queries
    def get_with_relations(self, conversation_id: int) -> List[Message]:
        return self.db.query(Message).join(User).join(Agent).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.status == 1
            )
        ).order_by(Message.created_at.asc()).all()
    
    def get_conversation_statistics(self, conversation_id: int) -> dict:
        total_messages = self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.status == 1
            )
        ).count()
        
        user_messages = self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.user_id.isnot(None),
                Message.status == 1
            )
        ).count()
        
        agent_messages = self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.agent_id.isnot(None),
                Message.status == 1
            )
        ).count()
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "agent_messages": agent_messages
        }