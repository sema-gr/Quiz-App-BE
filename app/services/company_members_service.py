from uuid import UUID
from app.models.company_member import CompanyMember, MembershipStatus
from app.uow.unit_of_work import UnitOfWork
from app.core.exceptions import (
    MemberAlreadyExists,
    InvitationNotFound,
    RequestNotFound,
    MemberNotFound,
)


class CompanyMembershipService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def invite_user(self, owner_id: UUID, company_id: UUID, target_user_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)

            if await self.uow.company_members.exists(target_user_id, company_id):
                raise MemberAlreadyExists()

            invitation = CompanyMember(
                company_id=company_id,
                user_id=target_user_id,
                status=MembershipStatus.INVITED,
            )
            await self.uow.company_members.create(invitation)
            return invitation

    async def cancel_invitation(self, owner_id: UUID, company_id: UUID, user_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)

            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.INVITED:
                raise InvitationNotFound()

            await self.uow.company_members.delete(member)

    async def accept_invitation(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.INVITED:
                raise InvitationNotFound()

            member.status = MembershipStatus.MEMBER
            await self.uow.company_members.update(member)
            return member

    async def decline_invitation(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.INVITED:
                raise InvitationNotFound()

            await self.uow.company_members.delete(member)

    async def request_to_join(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            if await self.uow.company_members.exists(user_id, company_id):
                raise MemberAlreadyExists()

            request = CompanyMember(
                company_id=company_id,
                user_id=user_id,
                status=MembershipStatus.REQUESTED,
            )
            await self.uow.company_members.create(request)
            return request

    async def cancel_request(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.REQUESTED:
                raise RequestNotFound()

            await self.uow.company_members.delete(member)

    async def approve_request(self, owner_id: UUID, company_id: UUID, user_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)

            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.REQUESTED:
                raise RequestNotFound()

            member.status = MembershipStatus.MEMBER
            await self.uow.company_members.update(member)
            return member

    async def reject_request(self, owner_id: UUID, company_id: UUID, user_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)

            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.REQUESTED:
                raise RequestNotFound()

            await self.uow.company_members.delete(member)

    async def remove_member(self, owner_id: UUID, company_id: UUID, user_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)

            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.MEMBER:
                raise MemberNotFound()

            await self.uow.company_members.delete(member)

    async def leave_company(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            member = await self.uow.company_members.get_by_user_and_company(
                user_id, company_id
            )
            if not member or member.status != MembershipStatus.MEMBER:
                raise MemberNotFound()

            await self.uow.company_members.delete(member)

    async def list_invitations(self, user_id: UUID):
        async with self.uow:
            return await self.uow.company_members.get_user_invitations(user_id)

    async def list_requests_for_owner(self, owner_id: UUID, company_id: UUID):
        async with self.uow:
            await self.uow.get_owned_company(owner_id, company_id)
            return await self.uow.company_members.get_company_requests(company_id)

    async def list_members(self, company_id: UUID, skip: int = 0, limit: int = 10):
        async with self.uow:
            return await self.uow.company_members.get_all_members(
                company_id, skip, limit
            )
