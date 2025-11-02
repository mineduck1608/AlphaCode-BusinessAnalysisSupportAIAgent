from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.conversation_agent import ConversationAgentRepository
from api.core.models import ConversationAgent


class ConversationAgentService:
    def __init__(self):
        self.repository = ConversationAgentRepository()

    async def create(
        self,
        db: AsyncSession,
        conversation_id: int,
        agent_id: int,
        is_active: bool = True
    ) -> ConversationAgent:
        # TODO: Validate conversation and agent exist

        ca = ConversationAgent(
            conversation_id=conversation_id,
            agent_id=agent_id,
            is_active=is_active,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create(db, ca)

    async def get_by_id(self, db: AsyncSession, ca_id: int) -> Optional[ConversationAgent]:
        return await self.repository.get_by_id(db, ca_id)

    async def list_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversationAgent]:
        return await self.repository.list_by_conversation(db, conversation_id, skip, limit)

    async def list_by_agent(
        self,
        db: AsyncSession,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversationAgent]:
        return await self.repository.list_by_agent(db, agent_id, skip, limit)

    async def list_active_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: int
    ) -> List[ConversationAgent]:
        return await self.repository.list_active_by_conversation(db, conversation_id)

    async def update(
        self,
        db: AsyncSession,
        ca_id: int,
        is_active: Optional[bool] = None
    ) -> Optional[ConversationAgent]:
        ca = await self.repository.get_by_id(db, ca_id)
        if not ca:
            return None

        if is_active is not None:
            ca.is_active = is_active
            ca.last_updated = datetime.utcnow()

        return await self.repository.update(db, ca)

    async def delete(self, db: AsyncSession, ca_id: int) -> bool:
        ca = await self.repository.get_by_id(db, ca_id)
        if not ca:
            return False
        await self.repository.delete(db, ca)
        return True

    async def deactivate_all(self, db: AsyncSession, conversation_id: int) -> List[ConversationAgent]:
        """Deactivate all agents in a conversation. Useful before adding a new active agent."""
        return await self.repository.deactivate_all_in_conversation(db, conversation_id)

    async def switch_active_agent(
        self,
        db: AsyncSession,
        conversation_id: int,
        agent_id: int
    ) -> ConversationAgent:
        """Deactivate all agents and set a new one as active."""
        await self.deactivate_all(db, conversation_id)
        
        # Check if agent is already in conversation
        agents = await self.list_by_conversation(db, conversation_id)
        for agent in agents:
            if agent.agent_id == agent_id:
                agent.is_active = True
                agent.last_updated = datetime.utcnow()
                return await self.repository.update(db, agent)
        
        # If not found, create new
        return await self.create(db, conversation_id, agent_id, is_active=True)