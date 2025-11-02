from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.services.conversation_agent import ConversationAgentService
from api.core.db import get_session
from api.core import schemas

service = ConversationAgentService()

router = APIRouter(
    prefix="/conversation-agents",
    tags=["conversation_agent"],
)

@router.post("/{conversation_id}/agents", response_model=schemas.ConversationAgent)
async def create_conversation_agent(
    conversation_id: int,
    agent_id: int,
    is_active: bool = True,
    db: AsyncSession = Depends(get_session)
) -> schemas.ConversationAgent:
    """Add an agent to a conversation."""
    return await service.create(
        db,
        conversation_id=conversation_id,
        agent_id=agent_id,
        is_active=is_active
    )


@router.get("/{ca_id}", response_model=schemas.ConversationAgent)
async def get_conversation_agent(
    ca_id: int,
    db: AsyncSession = Depends(get_session)
) -> schemas.ConversationAgent:
    """Get a specific conversation agent by ID."""
    ca = await service.get_by_id(db, ca_id)
    if not ca:
        raise HTTPException(status_code=404, detail="ConversationAgent not found")
    return ca


@router.get("/conversation/{conversation_id}", response_model=List[schemas.ConversationAgent])
async def list_by_conversation(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.ConversationAgent]:
    """List all agents in a conversation."""
    return await service.list_by_conversation(db, conversation_id, skip, limit)


@router.get("/agent/{agent_id}", response_model=List[schemas.ConversationAgent])
async def list_by_agent(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.ConversationAgent]:
    """List all conversations an agent is part of."""
    return await service.list_by_agent(db, agent_id, skip, limit)


@router.get("/conversation/{conversation_id}/active", response_model=List[schemas.ConversationAgent])
async def list_active_agents(
    conversation_id: int,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.ConversationAgent]:
    """List only active agents in a conversation."""
    return await service.list_active_by_conversation(db, conversation_id)


@router.put("/{ca_id}", response_model=schemas.ConversationAgent)
async def update_conversation_agent(
    ca_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_session)
) -> schemas.ConversationAgent:
    """Update a conversation agent's active status."""
    ca = await service.update(db, ca_id, is_active=is_active)
    if not ca:
        raise HTTPException(status_code=404, detail="ConversationAgent not found")
    return ca


@router.delete("/{ca_id}", status_code=204)
async def delete_conversation_agent(
    ca_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    """Remove an agent from a conversation."""
    deleted = await service.delete(db, ca_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ConversationAgent not found")


@router.post("/conversation/{conversation_id}/switch/{agent_id}", response_model=schemas.ConversationAgent)
async def switch_active_agent(
    conversation_id: int,
    agent_id: int,
    db: AsyncSession = Depends(get_session)
) -> schemas.ConversationAgent:
    """Deactivate all agents and set a specific one as active."""
    return await service.switch_active_agent(db, conversation_id, agent_id)
