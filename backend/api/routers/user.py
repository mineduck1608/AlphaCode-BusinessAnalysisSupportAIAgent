from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.services.user import UserService
from api.core.db import get_session
from api.core import schemas


router = APIRouter(prefix="/users", tags=["users"])
service = UserService()

@router.post("/", response_model=schemas.User)
async def create_user(
    email: str,
    password: str,
    role_id: int,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    return await service.create_user(db, email=email, password=password, role_id=role_id)

@router.get("/", response_model=List[schemas.User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.User]:
    return await service.list_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)) -> schemas.User:
    user = await service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int, 
    email: Optional[str] = None, 
    password: Optional[str] = None,
    role_id: Optional[int] = None,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    user = await service.update_user(db, user_id, email=email, password=password, role_id=role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
