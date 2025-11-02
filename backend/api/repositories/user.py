from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.models import User

class UserRepository:
    # CREATE
    async def create_user(self, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # READ (One)
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    # READ (By Email - Thêm vào để tiện cho xác thực)
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    # READ (All)
    async def list_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # UPDATE
    async def update_user(self, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # DELETE
    async def delete_user(self, db: AsyncSession, user: User) -> None:
        await db.delete(user)
        await db.commit()