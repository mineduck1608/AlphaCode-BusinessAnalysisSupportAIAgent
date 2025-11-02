from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.role import RoleRepository
from ...core.models import Role


class RoleService:
    def __init__(self):
        self.repository = RoleRepository()

    # CREATE
    async def create_role(self, db: AsyncSession, name: str) -> Role:
        role = Role(
            name=name,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create_role(db, role)

    # READ (One)
    async def get_role(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        return await self.repository.get_role(db, role_id)

    # READ (All)
    async def list_roles(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
        return await self.repository.list_roles(db, skip=skip, limit=limit)

    # UPDATE
    async def update_role(self, db: AsyncSession, role_id: int, name: Optional[str] = None) -> Optional[Role]:
        role = await self.repository.get_role(db, role_id)
        if not role:
            return None

        if name is not None:
            role.name = name
        
        role.last_updated = datetime.utcnow()
        return await self.repository.update_role(db, role)

    # DELETE
    async def delete_role(self, db: AsyncSession, role_id: int) -> bool:
        role = await self.repository.get_role(db, role_id)
        if not role:
            return False
        await self.repository.delete_role(db, role)
        return True