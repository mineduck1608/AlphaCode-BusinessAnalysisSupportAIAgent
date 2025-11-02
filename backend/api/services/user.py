from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
# Giả định có hàm hash password
# from ...core.security import get_password_hash 

from ..repositories.user import UserRepository
from ...core.models import User


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    # CREATE
    async def create_user(
        self, 
        db: AsyncSession, 
        email: str, 
        password: str, 
        role_id: int
    ) -> User:
        # Giả định: Kiểm tra user đã tồn tại (optional) và hash password
        # hashed_password = get_password_hash(password) 

        user = User(
            email=email,
            password=password, # Thay bằng hashed_password
            role_id=role_id,
            created_at=datetime.utcnow(),
            status=1,
            last_updated=None
        )
        return await self.repository.create_user(db, user)

    # READ (One)
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        return await self.repository.get_user(db, user_id)

    # READ (All)
    async def list_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.repository.list_users(db, skip=skip, limit=limit)

    # UPDATE
    async def update_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        email: Optional[str] = None, 
        password: Optional[str] = None,
        role_id: Optional[int] = None
    ) -> Optional[User]:
        user = await self.repository.get_user(db, user_id)
        if not user:
            return None

        if email is not None:
            user.email = email
        
        if password is not None:
            # user.password = get_password_hash(password) # Cần hash
            user.password = password 

        if role_id is not None:
            user.role_id = role_id
        
        user.last_updated = datetime.utcnow()
        return await self.repository.update_user(db, user)

    # DELETE
    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.repository.get_user(db, user_id)
        if not user:
            return False
        await self.repository.delete_user(db, user)
        return True