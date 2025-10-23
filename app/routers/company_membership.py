from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_user, get_company_members_service
from app.models.user import User
from app.schemas.company import CompanyMemberRead
from app.services.company_members import CompanyMembershipService

router = APIRouter(prefix="/companies/{company_id}", tags=["Company Membership"])


@router.post("/invite/accept")  # +
async def accept_invitation(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.accept_invitation(current_user.id, company_id)


@router.delete("/invite/decline")  # +
async def decline_invitation(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.decline_invitation(current_user.id, company_id)
    return {"detail": "Invitation declined"}


@router.post("/invite/{user_id}", response_model=CompanyMemberRead)  # +
async def invite_user(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.invite_user(current_user.id, company_id, user_id)


@router.delete("/invite/{user_id}")  # +
async def cancel_invitation(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.cancel_invitation(current_user.id, company_id, user_id)
    return {"detail": "Invitation canceled"}


# --------------------------------------


@router.post("/request", response_model=CompanyMemberRead)  # +
async def request_to_join(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.request_to_join(current_user.id, company_id)


@router.delete("/request")  # +
async def cancel_request(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.cancel_request(current_user.id, company_id)
    return {"detail": "Request canceled"}


@router.post("/request/approve/{user_id}")  # +
async def approve_request(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.approve_request(current_user.id, company_id, user_id)


@router.delete("/request/reject/{user_id}")  # +
async def reject_request(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.reject_request(current_user.id, company_id, user_id)
    return {"detail": "Request rejected"}


# --------------------------------------


@router.delete("/members/leave")  # +
async def leave_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.leave_company(current_user.id, company_id)
    return {"detail": "Left the company"}


@router.delete("/members/{user_id}")  # +
async def remove_member(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    await service.remove_member(current_user.id, company_id, user_id)
    return {"detail": "Member removed"}


# --------------------------------------


@router.get("/invitations", response_model=list[CompanyMemberRead])  # +
async def list_invitations(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_invitations(current_user.id)


@router.get("/requests", response_model=list[CompanyMemberRead])  # +
async def list_requests_for_owner(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_requests_for_owner(current_user.id, company_id)


@router.get("/members", response_model=list[CompanyMemberRead])  # +
async def list_members(
    company_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_members(company_id, skip, limit)
