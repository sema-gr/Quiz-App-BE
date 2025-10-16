from app.models.company import Company
from app.repository.base_repository import BaseRepository
from sqlalchemy.future import select


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db):
        super().__init__(Company, db)

    async def list(self, skip: int = 0, limit: int = 100):
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
