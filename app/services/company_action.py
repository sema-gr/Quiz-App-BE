from uuid import UUID
from app.models.company_action import CompanyAction, MembershipAction, MembershipStatus
from app.models.company_association import CompanyAssociation
from app.services.company import CompanyService
from app.core.exceptions import (
    MemberAlreadyExists,
    InvitationNotFound,
    RequestNotFound,
    MemberNotFound,
)
from app.uow.unit_of_work import UnitOfWork


class CompanyActionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.company_service = CompanyService(uow)

    async def handle_action(
        self,
        user_id: UUID,
        company_id: UUID,
        target_user_id: UUID | None,
        action_type: str,
        role_check: bool = False,
    ):
        if action_type in {"invite", "request"}:
            if target_user_id is None:
                target_user_id = user_id
            if await self.uow.company_actions.exists(target_user_id, company_id):
                raise MemberAlreadyExists

            assoc = CompanyAssociation(
                user_id=target_user_id, company_id=company_id, role="member"
            )
            await self.uow.company_actions.create(assoc)

            action_enum = (
                MembershipAction.INVITE
                if action_type == "invite"
                else MembershipAction.REQUEST
            )
            action = CompanyAction(
                association_id=assoc.id,
                action_type=action_enum,
                performed_by_id=user_id,
                status=MembershipStatus.PENDING,
            )
            await self.uow.company_actions.create(action)
            return action

        status_map = {
            "accept": MembershipStatus.ACCEPTED,
            "decline": MembershipStatus.REJECTED,
            "cancel": MembershipStatus.CANCELLED,
            "reject": MembershipStatus.REJECTED,
        }

        status = status_map.get(action_type)
        if status is None:
            raise ValueError("Unknown action type")

        if action_type in {"accept", "decline", "cancel"}:
            action = await self.uow.company_actions.get_pending_invite(
                target_user_id, company_id
            )
            if not action:
                raise InvitationNotFound
        else:
            action = await self.uow.company_actions.get_pending_request(
                target_user_id, company_id
            )
            if not action:
                raise RequestNotFound

        action.status = status
        return action

    async def remove_or_leave(
        self, user_id: UUID, company_id: UUID, target_user_id: UUID | None = None
    ):
        target_id = target_user_id or user_id
        action = await self.uow.company_actions.get_by_association(target_id)
        if not action:
            raise MemberNotFound
        action.status = MembershipStatus.REJECTED
        return action

    async def list_invitations(self, user_id: UUID):
        return await self.uow.company_actions.get_user_pending_invitations(user_id)

    async def list_requests_for_owner(self, owner_id: UUID, company_id: UUID):
        await self.company_service._get_owned_company(owner_id, company_id)
        return await self.uow.company_actions.get_company_pending_requests(company_id)
