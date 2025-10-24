from app.models.company_association import CompanyAssociation
from app.repository.base import BaseRepository
from sqlalchemy import select


class CompanyAssociationRepository(BaseRepository[CompanyAssociation]):
    def __init__(self, session):
        super().__init__(CompanyAssociation, session)

    async def get_by_user_and_company(
        self, user_id, company_id
    ) -> CompanyAssociation | None:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def exists(self, user_id, company_id) -> bool:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None
