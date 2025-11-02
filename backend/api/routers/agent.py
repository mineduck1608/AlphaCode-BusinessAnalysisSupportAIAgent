from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.services.agent import AgentService
from api.core.db import get_session
from api.core import schemas

service = AgentService()


router = APIRouter(
    prefix="/agents",
    tags=["agent"],
)

@router.post("/", response_model=schemas.Agent)
async def create_agent(
    name: str, 
    provider: str, 
    model: str, 
    avatar_url: str, 
    prompt_id: int, 
    db: AsyncSession = Depends(get_session)
) -> schemas.Agent:
    return await service.create_agent(
        db, 
        name=name, 
        provider=provider, 
        model=model, 
        avatar_url=avatar_url, 
        prompt_id=prompt_id
    )

@router.get("/", response_model=List[schemas.Agent])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.Agent]:
    return await service.list_agents(db, skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=schemas.Agent)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_session)) -> schemas.Agent:
    agent = await service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=schemas.Agent)
async def update_agent(
    agent_id: int, 
    name: Optional[str] = None, 
    provider: Optional[str] = None, 
    model: Optional[str] = None, 
    avatar_url: Optional[str] = None, 
    prompt_id: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_session)
) -> schemas.Agent:
    agent = await service.update_agent(
        db, 
        agent_id, 
        name=name, 
        provider=provider, 
        model=model, 
        avatar_url=avatar_url, 
        prompt_id=prompt_id,
        status=status
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_agent(db, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")