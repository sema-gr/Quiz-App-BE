from typing import Optional
from sqlalchemy import select
from app.models.company_action import CompanyAction, MembershipAction, MembershipStatus
from app.models.company_association import CompanyAssociation
from app.repository.base import BaseRepository
from uuid import UUID


class CompanyActionRepository(BaseRepository[CompanyAction]):
    def __init__(self, session):
        super().__init__(CompanyAction, session)

    async def get_by_association(self, association_id: UUID) -> Optional[CompanyAction]:
        stmt = select(self.model).where(self.model.association_id == association_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def _get_pending_action(
        self, user_id: UUID, company_id: UUID, action_type: MembershipAction
    ) -> Optional[CompanyAction]:
        stmt = (
            select(self.model)
            .join(
                CompanyAssociation, CompanyAssociation.id == self.model.association_id
            )
            .where(
                self.model.action_type == action_type,
                self.model.status == MembershipStatus.PENDING,
                CompanyAssociation.user_id == user_id,
                CompanyAssociation.company_id == company_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_pending_invite(
        self, user_id: UUID, company_id: UUID
    ) -> Optional[CompanyAction]:
        return await self._get_pending_action(
            user_id, company_id, MembershipAction.INVITE
        )

    async def get_pending_request(
        self, user_id: UUID, company_id: UUID
    ) -> Optional[CompanyAction]:
        return await self._get_pending_action(
            user_id, company_id, MembershipAction.REQUEST
        )
