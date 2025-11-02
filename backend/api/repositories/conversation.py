from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.models import Conversation, ConversationAgent  # phải là SQLAlchemy Base model


class ConversationRepository:
    async def create_conversation(self, db: AsyncSession, convo: Conversation) -> Conversation:
        db.add(convo)
        await db.commit()
        await db.refresh(convo)
        return convo

    async def get_conversation(self, db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_conversation_by_user_id(self, db: AsyncSession, user_id: int) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def list_conversations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Conversation]:
        stmt = select(Conversation).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_conversation(self, db: AsyncSession, convo: Conversation) -> Conversation:
        db.add(convo)
        await db.commit()
        await db.refresh(convo)
        return convo

    async def delete_conversation(self, db: AsyncSession, convo: Conversation) -> None:
        await db.delete(convo)
        await db.commit()

    async def create_conversation_agent(self, db: AsyncSession, ca: ConversationAgent) -> ConversationAgent:
        db.add(ca)
        await db.commit()
        await db.refresh(ca)
        return ca

    async def get_conversation_agent(self, db: AsyncSession, ca_id: int) -> Optional[ConversationAgent]:
        stmt = select(ConversationAgent).where(ConversationAgent.id == ca_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversation_agents_by_conversation(
        self, db: AsyncSession, conversation_id: int
    ) -> List[ConversationAgent]:
        stmt = select(ConversationAgent).where(ConversationAgent.conversation_id == conversation_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_conversation_agent(self, db: AsyncSession, ca: ConversationAgent) -> ConversationAgent:
        db.add(ca)
        await db.commit()
        await db.refresh(ca)
        return ca

    async def delete_conversation_agent(self, db: AsyncSession, ca: ConversationAgent) -> None:
        await db.delete(ca)
        await db.commit()
