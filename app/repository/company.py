import uuid
from sqlalchemy import select
from app.models.company import Company
from app.models.company_action import CompanyAction
from app.models.company_association import CompanyAssociation
from app.models.enum import MembershipAction, MembershipStatus
from app.repository.base import BaseRepository
from app.schemas.company import CompanyMemberRead


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, sessions):
        super().__init__(Company, sessions)

    async def get_pending_requests(self, company_id: uuid.UUID, skip=0, limit=10):
        stmt = (
            select(CompanyAssociation, CompanyAction.status)
            .join(CompanyAction, CompanyAssociation.id == CompanyAction.association_id)
            .where(
                CompanyAssociation.company_id == company_id,
                CompanyAction.status == MembershipStatus.ACCEPTED,
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        members = []
        for assoc, status in rows:
            members.append(
                CompanyMemberRead(
                    company_id=assoc.company_id,
                    user_id=assoc.user_id,
                    status=status.value,
                    created_at=assoc.created_at,
                )
            )
        return members
