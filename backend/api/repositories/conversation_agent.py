from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.models import ConversationAgent


class ConversationAgentRepository:
    async def create(self, db: AsyncSession, conversation_agent: ConversationAgent) -> ConversationAgent:
        db.add(conversation_agent)
        await db.commit()
        await db.refresh(conversation_agent)
        return conversation_agent

    async def get_by_id(self, db: AsyncSession, ca_id: int) -> Optional[ConversationAgent]:
        result = await db.execute(
            select(ConversationAgent).where(ConversationAgent.id == ca_id)
        )
        return result.scalar_one_or_none()

    async def list_by_conversation(
        self, 
        db: AsyncSession, 
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversationAgent]:
        result = await db.execute(
            select(ConversationAgent)
            .where(ConversationAgent.conversation_id == conversation_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
        
    async def list_by_agent(
        self,
        db: AsyncSession,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversationAgent]:
        result = await db.execute(
            select(ConversationAgent)
            .where(ConversationAgent.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def list_active_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: int
    ) -> List[ConversationAgent]:
        result = await db.execute(
            select(ConversationAgent).where(
                ConversationAgent.conversation_id == conversation_id,
                ConversationAgent.is_active == True,
                ConversationAgent.status == 1
            )
        )
        return result.scalars().all()

    async def update(self, db: AsyncSession, conversation_agent: ConversationAgent) -> ConversationAgent:
        db.add(conversation_agent)
        await db.commit()
        await db.refresh(conversation_agent)
        return conversation_agent

    async def delete(self, db: AsyncSession, conversation_agent: ConversationAgent) -> None:
        await db.delete(conversation_agent)
        await db.commit()

    async def deactivate_all_in_conversation(
        self,
        db: AsyncSession,
        conversation_id: int
    ) -> List[ConversationAgent]:
        agents = await self.list_active_by_conversation(db, conversation_id)
        for agent in agents:
            agent.is_active = False
            agent.last_updated = __import__('datetime').datetime.utcnow()
            db.add(agent)
        await db.commit()
        return agents