from typing import List, Tuple, Optional
from sqlalchemy import select
from app.models.company_association import CompanyAssociation
from app.models.company_action import CompanyAction, MembershipAction, MembershipStatus
from app.repository.base import BaseRepository
from uuid import UUID


class CompanyAssociationRepository(BaseRepository[CompanyAssociation]):
    def __init__(self, session):
        super().__init__(CompanyAssociation, session)

    async def get_by_user_and_company(
        self, user_id: UUID, company_id: UUID
    ) -> Optional[CompanyAssociation]:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.company_id == company_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def exists(self, user_id: UUID, company_id: UUID) -> bool:
        return (await self.get_by_user_and_company(user_id, company_id)) is not None

    async def _get_assocs_with_action(
        self,
        company_id: UUID = None,
        user_id: UUID = None,
        role: str = None,
        action_type: MembershipAction = None,
        status: MembershipStatus = None,
    ) -> List[Tuple[CompanyAssociation, MembershipStatus]]:
        stmt = select(self.model, CompanyAction.status).join(
            CompanyAction, CompanyAction.association_id == self.model.id
        )

        if company_id:
            stmt = stmt.where(self.model.company_id == company_id)
        if user_id:
            stmt = stmt.where(self.model.user_id == user_id)
        if role:
            stmt = stmt.where(self.model.role == role)
        if action_type:
            stmt = stmt.where(CompanyAction.action_type == action_type)
        if status:
            stmt = stmt.where(CompanyAction.status == status)

        result = await self.session.execute(stmt)
        return result.all()

    async def get_all_by_role(
        self, company_id: UUID, role: str
    ) -> List[Tuple[CompanyAssociation, MembershipStatus]]:
        return await self._get_assocs_with_action(company_id=company_id, role=role)

    async def get_user_pending_invitations(
        self, user_id: UUID
    ) -> List[Tuple[CompanyAssociation, MembershipStatus]]:
        return await self._get_assocs_with_action(
            user_id=user_id,
            action_type=MembershipAction.INVITE,
            status=MembershipStatus.PENDING,
        )

    async def get_company_pending_requests(
        self, company_id: UUID
    ) -> List[Tuple[CompanyAssociation, MembershipStatus]]:
        return await self._get_assocs_with_action(
            company_id=company_id,
            action_type=MembershipAction.REQUEST,
            status=MembershipStatus.PENDING,
        )

    async def list(self, company_id=None) -> List[CompanyAssociation]:
        query = select(CompanyAssociation)
        if company_id is not None:
            query = query.where(CompanyAssociation.company_id == company_id)
        result = await self.session.execute(query)
        return result.scalars().all()
