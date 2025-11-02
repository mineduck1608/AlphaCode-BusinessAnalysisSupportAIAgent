from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.repositories.prompt import PromptRepository
from api.core.models import Prompt


class PromptService:
    def __init__(self):
        self.repository = PromptRepository()

    # CREATE
    async def create_prompt(self, db: AsyncSession, name: str, content: str) -> Prompt:
        prompt = Prompt(
            name=name,
            content=content,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create_prompt(db, prompt)

    # READ (One)
    async def get_prompt(self, db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
        return await self.repository.get_prompt(db, prompt_id)

    # READ (All)
    async def list_prompts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Prompt]:
        return await self.repository.list_prompts(db, skip=skip, limit=limit)

    # UPDATE
    async def update_prompt(
        self, 
        db: AsyncSession, 
        prompt_id: int, 
        name: Optional[str] = None, 
        content: Optional[str] = None
    ) -> Optional[Prompt]:
        prompt = await self.repository.get_prompt(db, prompt_id)
        if not prompt:
            return None

        if name is not None:
            prompt.name = name
        if content is not None:
            prompt.content = content
        
        prompt.last_updated = datetime.utcnow()
        return await self.repository.update_prompt(db, prompt)

    # DELETE
    async def delete_prompt(self, db: AsyncSession, prompt_id: int) -> bool:
        prompt = await self.repository.get_prompt(db, prompt_id)
        if not prompt:
            return False
        await self.repository.delete_prompt(db, prompt)
        return True