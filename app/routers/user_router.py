from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
)
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_user_by_id(db, user_id)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_route(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_route(
    user_id: UUID,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_user(db, user_id, update_data)


@router.delete("/{user_id}", status_code=404)
async def delete_user_route(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await delete_user(db, user_id)
