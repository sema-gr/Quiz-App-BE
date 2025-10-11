from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.core.security import hash_password
from app.core.logging import logger


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 10):
        users = await self.repo.get_all(skip=skip, limit=limit)
        logger.warning(f"Fetched {len(users)} users (skip={skip}, limit={limit})")
        return users

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.repo.get_by_field("id", user_id)
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found",
            )
        return user

    async def create(self, user_data: UserCreate) -> User:
        existing = await self.repo.get_by_field("email", user_data.email)
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

        created_user = await self.repo.create(new_user)
        logger.warning(
            f"User created: id={created_user.id}, email={created_user.email}"
        )
        return created_user

    async def update(
        self, user_id: UUID, update_data: UserUpdate, current_user: User
    ) -> User:
        if current_user.id != user_id:
            logger.warning(
                f"User {current_user.id} tried to update another user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile",
            )

        user = await self.get_by_id(user_id)

        if hasattr(update_data, "email") and update_data.email:
            logger.warning(f"User {user_id} attempted to change email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email cannot be changed",
            )

        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.password is not None:
            user.hashed_password = hash_password(update_data.password)

        updated_user = await self.repo.update(user)
        logger.warning(f"User updated: id={updated_user.id}")
        return updated_user

    async def delete(self, user_id: UUID, current_user: User):
        if current_user.id != user_id:
            logger.warning(
                f"User {current_user.id} tried to delete another user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own profile",
            )

        user = await self.get_by_id(user_id)
        await self.repo.delete(user)
        logger.warning(f"User deleted: id={user_id}")
        return {"detail": "User deleted successfully"}
