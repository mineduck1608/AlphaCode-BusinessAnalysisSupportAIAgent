from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.services.role import RoleService
from api.core.db import get_session
from api.core import schemas


service = RoleService()

router = APIRouter(
    prefix="/roles",
    tags=["role"],
)


@router.post("/", response_model=schemas.Role)
async def create_role(name: str, db: AsyncSession = Depends(get_session)) -> schemas.Role:
    return await service.create_role(db, name=name)

@router.get("/", response_model=List[schemas.Role])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.Role]:
    return await service.list_roles(db, skip=skip, limit=limit)

@router.get("/{role_id}", response_model=schemas.Role)
async def get_role(role_id: int, db: AsyncSession = Depends(get_session)) -> schemas.Role:
    role = await service.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=schemas.Role)
async def update_role(role_id: int, name: str, db: AsyncSession = Depends(get_session)) -> schemas.Role:
    role = await service.update_role(db, role_id, name=name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_session)) -> None:
    deleted = await service.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
