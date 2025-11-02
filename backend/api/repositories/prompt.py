from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.models import Prompt

class PromptRepository:
    # CREATE
    async def create_prompt(self, db: AsyncSession, prompt: Prompt) -> Prompt:
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        return prompt

    # READ (One)
    async def get_prompt(self, db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
        result = await db.execute(
            select(Prompt).where(Prompt.id == prompt_id)
        )
        return result.scalar_one_or_none()

    # READ (All)
    async def list_prompts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Prompt]:
        result = await db.execute(
            select(Prompt).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # UPDATE
    async def update_prompt(self, db: AsyncSession, prompt: Prompt) -> Prompt:
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        return prompt

    # DELETE
    async def delete_prompt(self, db: AsyncSession, prompt: Prompt) -> None:
        await db.delete(prompt)
        await db.commit()