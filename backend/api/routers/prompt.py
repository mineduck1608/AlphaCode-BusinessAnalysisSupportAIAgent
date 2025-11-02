# prompt.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.services.prompt import PromptService
from api.core.db import get_session
from api.core import schemas

service = PromptService()

router = APIRouter(
    prefix="/prompts",
    tags=["prompt"],
)

@router.post("/", response_model=schemas.Prompt)
async def create_prompt(
    prompt_data: schemas.PromptCreate,
    db: AsyncSession = Depends(get_session)
) -> schemas.Prompt:
    return await service.create_prompt(db, name=prompt_data.name, content=prompt_data.content)

@router.get("/", response_model=List[schemas.Prompt])
async def list_prompts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.Prompt]:
    return await service.list_prompts(db, skip=skip, limit=limit)

@router.get("/{prompt_id}", response_model=schemas.Prompt)
async def get_prompt(prompt_id: int, db: AsyncSession = Depends(get_session)) -> schemas.Prompt:
    prompt = await service.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.put("/{prompt_id}", response_model=schemas.Prompt)
async def update_prompt(
    prompt_id: int, 
    prompt_data: schemas.PromptUpdate,
    db: AsyncSession = Depends(get_session)
) -> schemas.Prompt:
    prompt = await service.update_prompt(db, prompt_id, name=prompt_data.name, content=prompt_data.content)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_prompt(db, prompt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")