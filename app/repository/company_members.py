from sqlalchemy import select
from app.models.company_associationand_actions import (
    CompanyAssociation,
    MembershipStatus,
)
from app.repository.base import BaseRepository


class CompanyMemberRepository(BaseRepository[CompanyAssociation]):
    def __init__(self, session):
        super().__init__(CompanyAssociation, session)

    async def get_by_user_and_company(self, user_id, company_id):
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

    async def get_user_invitations(self, user_id):
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == MembershipStatus.INVITED,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_company_requests(self, company_id):
        stmt = select(self.model).where(
            self.model.company_id == company_id,
            self.model.status == MembershipStatus.REQUESTED,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_members(self, company_id, skip=0, limit=10):
        stmt = (
            select(self.model)
            .where(
                self.model.company_id == company_id,
                self.model.status == MembershipStatus.MEMBER,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
