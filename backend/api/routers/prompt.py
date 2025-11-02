from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..services.prompt import PromptService
from api.core.db import get_session
from api.core.models import Prompt # Giả sử Prompt là một model/schema cho response


router = APIRouter(prefix="/prompts", tags=["prompts"])
service = PromptService()

@router.post("/", response_model=Prompt)
async def create_prompt(
    name: str, 
    content: str, 
    db: AsyncSession = Depends(get_session)
) -> Prompt:
    return await service.create_prompt(db, name=name, content=content)

@router.get("/", response_model=List[Prompt])
async def list_prompts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[Prompt]:
    return await service.list_prompts(db, skip=skip, limit=limit)

@router.get("/{prompt_id}", response_model=Prompt)
async def get_prompt(prompt_id: int, db: AsyncSession = Depends(get_session)) -> Prompt:
    prompt = await service.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.put("/{prompt_id}", response_model=Prompt)
async def update_prompt(
    prompt_id: int, 
    name: Optional[str] = None, 
    content: Optional[str] = None, 
    db: AsyncSession = Depends(get_session)
) -> Prompt:
    prompt = await service.update_prompt(db, prompt_id, name=name, content=content)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_prompt(db, prompt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")