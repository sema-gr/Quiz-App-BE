from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()
