from sqlalchemy import select
from app.models.company_action import CompanyAction, MembershipAction, MembershipStatus
from app.models.company_association import CompanyAssociation
from app.repository.base import BaseRepository


class CompanyActionRepository(BaseRepository[CompanyAction]):
    def __init__(self, session):
        super().__init__(CompanyAction, session)

    async def get_by_association(self, association_id):
        stmt = select(self.model).where(self.model.association_id == association_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_pending_invite(self, user_id, company_id):
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                self.model.action_type == MembershipAction.INVITE,
                self.model.status == MembershipStatus.PENDING,
                CompanyAssociation.user_id == user_id,
                CompanyAssociation.company_id == company_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_pending_request(self, user_id, company_id):
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                self.model.action_type == MembershipAction.REQUEST,
                self.model.status == MembershipStatus.PENDING,
                CompanyAssociation.user_id == user_id,
                CompanyAssociation.company_id == company_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_company_pending_requests(self, company_id):
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                self.model.action_type == MembershipAction.REQUEST,
                self.model.status == MembershipStatus.PENDING,
                CompanyAssociation.company_id == company_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_pending_invitations(self, user_id):
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                self.model.action_type == MembershipAction.INVITE,
                self.model.status == MembershipStatus.PENDING,
                CompanyAssociation.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists(self, user_id, company_id) -> bool:
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                CompanyAssociation.user_id == user_id,
                CompanyAssociation.company_id == company_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None
