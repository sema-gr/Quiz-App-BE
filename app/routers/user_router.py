from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await UserService(db).get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService(db).create(user_data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID, update_data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    return await UserService(db).update(user_id, update_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    await UserService(db).delete(user_id)
    return None
