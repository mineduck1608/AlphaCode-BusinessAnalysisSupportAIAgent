from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.models import Agent

class AgentRepository:
    # CREATE
    async def create_agent(self, db: AsyncSession, agent: Agent) -> Agent:
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent

    # READ (One)
    async def get_agent(self, db: AsyncSession, agent_id: int) -> Optional[Agent]:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    # READ (All)
    async def list_agents(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Agent]:
        result = await db.execute(
            select(Agent).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # UPDATE
    async def update_agent(self, db: AsyncSession, agent: Agent) -> Agent:
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent

    # DELETE
    async def delete_agent(self, db: AsyncSession, agent: Agent) -> None:
        await db.delete(agent)
        await db.commit()