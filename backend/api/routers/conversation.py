from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..services.conversation import ConversationService
from ...core.db import get_session
from ...core.models import Conversation, ConversationAgent

router = APIRouter(prefix="/conversations", tags=["conversations"])
service = ConversationService()


@router.post("/", response_model=Conversation)
async def create_conversation(
    name: str,
    user_id: int,
    is_shared: bool = False,
    summary: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
) -> Conversation:
    return await service.create_conversation(
        db,
        name=name,
        user_id=user_id,
        is_shared=is_shared,
        summary=summary
    )


@router.get("/", response_model=List[Conversation])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[Conversation]:
    return await service.list_conversations(db, skip=skip, limit=limit)


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_session)
) -> Conversation:
    convo = await service.get_conversation(db, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: int,
    name: Optional[str] = None,
    is_shared: Optional[bool] = None,
    summary: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
) -> Conversation:
    convo = await service.update_conversation(
        db,
        conversation_id,
        name=name,
        is_shared=is_shared,
        summary=summary
    )
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    deleted = await service.delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/{conversation_id}/agents", response_model=ConversationAgent)
async def add_agent_to_conversation(
    conversation_id: int,
    agent_id: int,
    is_active: bool = True,
    db: AsyncSession = Depends(get_session)
) -> ConversationAgent:
    return await service.create_conversation_agent(
        db,
        conversation_id=conversation_id,
        agent_id=agent_id,
        is_active=is_active
    )


@router.get("/{conversation_id}/agents", response_model=List[ConversationAgent])
async def list_conversation_agents(
    conversation_id: int,
    db: AsyncSession = Depends(get_session)
) -> List[ConversationAgent]:
    return await service.list_conversation_agents(db, conversation_id)


@router.put("/agents/{ca_id}", response_model=ConversationAgent)
async def update_conversation_agent(
    ca_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_session)
) -> ConversationAgent:
    ca = await service.update_conversation_agent(db, ca_id, is_active=is_active)
    if not ca:
        raise HTTPException(status_code=404, detail="Conversation Agent not found")
    return ca


@router.delete("/agents/{ca_id}", status_code=204)
async def delete_conversation_agent(
    ca_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    deleted = await service.delete_conversation_agent(db, ca_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation Agent not found")