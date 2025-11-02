from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.agent import AgentRepository
from ...core.models import Agent


class AgentService:
    def __init__(self):
        self.repository = AgentRepository()

    # CREATE
    async def create_agent(
        self, 
        db: AsyncSession, 
        name: str, 
        provider: str, 
        model: str, 
        avatar_url: str, 
        prompt_id: int
    ) -> Agent:
        agent = Agent(
            name=name,
            provider=provider,
            model=model,
            avatar_url=avatar_url,
            prompt_id=prompt_id,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create_agent(db, agent)

    # READ (One)
    async def get_agent(self, db: AsyncSession, agent_id: int) -> Optional[Agent]:
        return await self.repository.get_agent(db, agent_id)

    # READ (All)
    async def list_agents(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Agent]:
        return await self.repository.list_agents(db, skip=skip, limit=limit)

    # UPDATE
    async def update_agent(
        self, 
        db: AsyncSession, 
        agent_id: int, 
        name: Optional[str] = None, 
        provider: Optional[str] = None, 
        model: Optional[str] = None, 
        avatar_url: Optional[str] = None, 
        prompt_id: Optional[int] = None,
        status: Optional[int] = None
    ) -> Optional[Agent]:
        agent = await self.repository.get_agent(db, agent_id)
        if not agent:
            return None

        if name is not None:
            agent.name = name
        if provider is not None:
            agent.provider = provider
        if model is not None:
            agent.model = model
        if avatar_url is not None:
            agent.avatar_url = avatar_url
        if prompt_id is not None:
            agent.prompt_id = prompt_id
        if status is not None:
            agent.status = status
        
        agent.last_updated = datetime.utcnow()
        return await self.repository.update_agent(db, agent)

    # DELETE
    async def delete_agent(self, db: AsyncSession, agent_id: int) -> bool:
        agent = await self.repository.get_agent(db, agent_id)
        if not agent:
            return False
        await self.repository.delete_agent(db, agent)
        return True