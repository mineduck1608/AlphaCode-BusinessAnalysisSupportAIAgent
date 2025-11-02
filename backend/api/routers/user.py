# user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from api.services.user import UserService
from api.core.db import get_session
from api.core import schemas

router = APIRouter(
    prefix="/users",
    tags=["user"],
)

service = UserService()

@router.post("/", response_model=schemas.User)
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    return await service.create_user(db, email=user_data.email, password=user_data.password, role_id=user_data.role_id)

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
    user_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    user = await service.update_user(db, user_id, email=user_data.email, password=user_data.password, role_id=user_data.role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")