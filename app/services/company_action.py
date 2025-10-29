import datetime
from uuid import UUID
from typing import Optional, List
from app.models.company_action import CompanyAction, MembershipAction, MembershipStatus
from app.models.company_association import CompanyAssociation
from app.services.company import CompanyService
from app.core.exceptions import (
    MemberAlreadyExists,
    InvitationNotFound,
    RequestNotFound,
    MemberNotFound,
)
from app.schemas.company import CompanyMemberRead
from app.uow.unit_of_work import UnitOfWork


class CompanyActionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.company_service = CompanyService(uow)

    async def _build_member_read(
        self, assoc: CompanyAssociation, status: MembershipStatus
    ) -> CompanyMemberRead:
        return CompanyMemberRead(
            company_id=assoc.company_id,
            user_id=assoc.user_id,
            status=status,
            created_at=assoc.created_at or datetime.datetime(),
        )

    async def manage_invitation(
        self, admin_id: UUID, company_id: UUID, target_user_id: UUID, action: str
    ) -> CompanyMemberRead:
        await self.company_service._get_owned_company(admin_id, company_id)

        if action == "invite":
            return await self.create_invitation(admin_id, company_id, target_user_id)
        elif action == "cancel":
            return await self.cancel_invitation(admin_id, company_id, target_user_id)

        raise ValueError("Invalid action for invitation")

    async def create_invitation(
        self, admin_id: UUID, company_id: UUID, target_user_id: UUID
    ) -> CompanyMemberRead:
        if await self.uow.company_associations.exists(target_user_id, company_id):
            raise MemberAlreadyExists

        assoc = CompanyAssociation(
            user_id=target_user_id, company_id=company_id, role="member"
        )
        await self.uow.company_associations.create(assoc)

        action = CompanyAction(
            association_id=assoc.id,
            action_type=MembershipAction.INVITE,
            performed_by_id=admin_id,
            status=MembershipStatus.PENDING,
        )
        await self.uow.company_actions.create(action)

        return await self._build_member_read(assoc, action.status)

    async def create_join_request(
        self, user_id: UUID, company_id: UUID
    ) -> CompanyMemberRead:
        if await self.uow.company_associations.exists(user_id, company_id):
            raise MemberAlreadyExists
        assoc = CompanyAssociation(
            user_id=user_id, company_id=company_id, role="member"
        )
        await self.uow.company_associations.create(assoc)
        action = CompanyAction(
            association_id=assoc.id,
            action_type=MembershipAction.REQUEST,
            performed_by_id=user_id,
            status=MembershipStatus.PENDING,
        )
        await self.uow.company_actions.create(action)
        return await self._build_member_read(assoc, action.status)

    async def cancel_invitation(
        self, target_user_id: UUID, company_id: UUID
    ) -> CompanyMemberRead:
        action = await self.uow.company_actions.get_pending_invite(
            target_user_id, company_id
        )
        if not action:
            raise InvitationNotFound
        action.status = MembershipStatus.CANCELLED

        assoc = await self.uow.company_associations.get_by_field(
            "id", action.association_id
        )
        if not assoc:
            raise MemberNotFound

        return await self._build_member_read(assoc, action.status)

    async def cancel_join_request(
        self, user_id: UUID, company_id: UUID
    ) -> CompanyMemberRead:
        action = await self.uow.company_actions.get_pending_request(user_id, company_id)
        if not action:
            raise RequestNotFound
        action.status = MembershipStatus.CANCELLED

        assoc = await self.uow.company_associations.get_by_field(
            "id", action.association_id
        )
        if not assoc:
            raise MemberNotFound

        return await self._build_member_read(assoc, action.status)

    async def respond_to_invitation(
        self, user_id: UUID, company_id: UUID, action_str: str
    ) -> CompanyMemberRead:
        status = (
            MembershipStatus.ACCEPTED
            if action_str == "accept"
            else MembershipStatus.REJECTED
        )

        action = await self.uow.company_actions.get_pending_invite(user_id, company_id)
        if not action:
            raise InvitationNotFound

        action.status = status

        assoc = await self.uow.company_associations.get_by_field(
            "id", action.association_id
        )
        if not assoc:
            raise MemberNotFound("Пов'язане членство не знайдено")

        return await self._build_member_read(assoc, action.status)

    async def respond_to_join_request(
        self, admin_id: UUID, company_id: UUID, target_user_id: UUID, action_str: str
    ) -> CompanyMemberRead:
        await self.company_service._get_owned_company(admin_id, company_id)

        status = (
            MembershipStatus.ACCEPTED
            if action_str == "accept"
            else MembershipStatus.REJECTED
        )

        async with self.uow:
            action = await self.uow.company_actions.get_pending_request(
                target_user_id, company_id
            )
            if not action:
                raise RequestNotFound

            action.status = status

            assoc = await self.uow.company_associations.get_by_field(
                "id", action.association_id
            )
            if not assoc:
                raise MemberNotFound("Пов'язане членство не знайдено")

            return await self._build_member_read(assoc, action.status)

    async def manage_join_request(
        self, user_id: UUID, company_id: UUID, action: str
    ) -> CompanyMemberRead:
        async with self.uow:
            if action == "create":
                if await self.uow.company_associations.exists(user_id, company_id):
                    raise MemberAlreadyExists

                assoc = CompanyAssociation(
                    user_id=user_id, company_id=company_id, role="member"
                )
                await self.uow.company_associations.create(assoc)

                action_obj = CompanyAction(
                    association_id=assoc.id,
                    action_type=MembershipAction.REQUEST,
                    performed_by_id=user_id,
                    status=MembershipStatus.PENDING,
                )
                await self.uow.company_actions.create(action_obj)

                return await self._build_member_read(assoc, action_obj.status)

            elif action == "cancel":
                action_obj = await self.uow.company_actions.get_pending_request(
                    user_id, company_id
                )
                if not action_obj:
                    raise RequestNotFound

                action_obj.status = MembershipStatus.CANCELLED
                assoc = await self.uow.company_associations.get_by_field(
                    "id", action_obj.association_id
                )
                if not assoc:
                    raise MemberNotFound("Пов'язане членство не знайдено")

                return await self._build_member_read(assoc, action_obj.status)

            else:
                raise ValueError("Invalid action. Must be 'create' or 'cancel'.")

    async def list_invitations(self, user_id: UUID) -> List[CompanyMemberRead]:
        results = await self.uow.company_associations.get_user_pending_invitations(
            user_id
        )
        return [
            await self._build_member_read(assoc, status) for assoc, status in results
        ]

    async def list_requests_for_owner(
        self, owner_id: UUID, company_id: UUID
    ) -> List[CompanyMemberRead]:
        await self.company_service._get_owned_company(owner_id, company_id)
        results = await self.uow.company_associations.get_company_pending_requests(
            company_id
        )
        return [
            await self._build_member_read(assoc, status) for assoc, status in results
        ]

    async def list_admins(self, company_id: UUID) -> List[CompanyMemberRead]:
        results = await self.uow.company_associations.get_all_by_role(
            company_id, "admin"
        )
        return [
            await self._build_member_read(assoc, status) for assoc, status in results
        ]

    async def assign_admin(
        self, owner_id: UUID, company_id: UUID, target_user_id: UUID
    ) -> CompanyMemberRead:
        await self.company_service._get_owned_company(owner_id, company_id)
        async with self.uow:
            assoc = await self.uow.company_associations.get_by_user_and_company(
                target_user_id, company_id
            )
            if not assoc:
                raise MemberNotFound
            if assoc.role == "admin":
                raise MemberAlreadyExists
            assoc.role = "admin"

            action = await self.uow.company_actions.get_by_association(assoc.id)
            return await self._build_member_read(
                assoc, action.status if action else MembershipStatus.ACCEPTED
            )

    async def remove_admin(
        self, owner_id: UUID, company_id: UUID, target_user_id: UUID
    ) -> CompanyMemberRead:
        await self.company_service._get_owned_company(owner_id, company_id)
        async with self.uow:
            assoc = await self.uow.company_associations.get_by_user_and_company(
                target_user_id, company_id
            )
            if not assoc or assoc.role != "admin":
                raise MemberNotFound
            assoc.role = "member"

            action = await self.uow.company_actions.get_by_association(assoc.id)
            return await self._build_member_read(
                assoc, action.status if action else MembershipStatus.ACCEPTED
            )

    async def remove_or_leave(
        self, user_id: UUID, company_id: UUID, target_user_id: Optional[UUID] = None
    ) -> CompanyMemberRead:
        target_id = target_user_id or user_id
        assoc = await self.uow.company_associations.get_by_user_and_company(
            target_id, company_id
        )
        if not assoc:
            raise MemberNotFound

        action = await self.uow.company_actions.get_by_association(assoc.id)
        if action:
            action.status = MembershipStatus.REJECTED

        await self.uow.company_associations.delete(assoc)
        return await self._build_member_read(
            assoc, action.status if action else MembershipStatus.REJECTED
        )
