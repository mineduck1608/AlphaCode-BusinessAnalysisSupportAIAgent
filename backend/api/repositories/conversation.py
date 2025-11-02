from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.models import Conversation, ConversationAgent


class ConversationRepository:
    async def create_conversation(self, db: AsyncSession, convo: Conversation) -> Conversation:
        db.add(convo)
        await db.commit()
        await db.refresh(convo)
        return convo

    async def get_conversation(self, db: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Conversation]:
        result = await db.execute(
            select(Conversation).offset(skip).limit(limit)
        )
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
        result = await db.execute(
            select(ConversationAgent).where(ConversationAgent.id == ca_id)
        )
        return result.scalar_one_or_none()

    async def list_conversation_agents_by_conversation(
        self, db: AsyncSession, conversation_id: int
    ) -> List[ConversationAgent]:
        result = await db.execute(
            select(ConversationAgent).where(
                ConversationAgent.conversation_id == conversation_id
            )
        )
        return result.scalars().all()

    async def update_conversation_agent(self, db: AsyncSession, ca: ConversationAgent) -> ConversationAgent:
        db.add(ca)
        await db.commit()
        await db.refresh(ca)
        return ca

    async def delete_conversation_agent(self, db: AsyncSession, ca: ConversationAgent) -> None:
        await db.delete(ca)
        await db.commit()