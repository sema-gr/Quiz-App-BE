from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by_field("email", email)
