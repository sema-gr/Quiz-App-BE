from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.core.logging import logger


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        logger.info(f"Fetched {len(users)} users (skip={skip}, limit={limit})")
        return users

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found",
            )
        return user

    async def create(self, user_data: UserCreate):
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing = result.scalars().first()
        if existing:
            logger.warning(
                f"Attempt to register with existing email: {user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info(f"User created: id={new_user.id}, email={new_user.email}")
        return new_user

    async def update(self, user_id: UUID, update_data: UserUpdate):
        user = await self.get_by_id(user_id)

        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.password is not None:
            user.hashed_password = hash_password(update_data.password)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User updated: id={user.id}")
        return user

    async def delete(self, user_id: UUID):
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()
        logger.warning(f"User deleted: id={user_id}")
        return {"detail": "User deleted successfully"}
