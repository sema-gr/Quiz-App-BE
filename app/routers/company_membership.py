from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_user, get_company_members_service
from app.models.user import User
from app.schemas.company import CompanyMemberRead
from app.services.company_members import CompanyMembershipService

router = APIRouter(prefix="/companies/{company_id}", tags=["Company Membership"])


@router.post("/invitations/{user_id}", response_model=CompanyMemberRead)
async def manage_invitation(
    company_id: UUID,
    user_id: UUID,
    action: str = Query(..., regex="^(invite|cancel)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    if action == "invite":
        return await service.invite_user(current_user.id, company_id, user_id)
    else:
        await service.cancel_invitation(current_user.id, company_id, user_id)
        return {"detail": "Invitation canceled"}


@router.post("/invitations/accept-decline")
async def accept_decline_invitation(
    company_id: UUID,
    action: str = Query(..., regex="^(accept|decline)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    if action == "accept":
        return await service.accept_invitation(current_user.id, company_id)
    else:
        await service.decline_invitation(current_user.id, company_id)
        return {"detail": "Invitation declined"}


@router.post("/requests")
async def manage_join_request(
    company_id: UUID,
    action: str = Query(..., regex="^(create|cancel)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    if action == "create":
        return await service.request_to_join(current_user.id, company_id)
    else:
        await service.cancel_request(current_user.id, company_id)
        return {"detail": "Request canceled"}


@router.post("/requests/{user_id}")
async def manage_join_request_approval(
    company_id: UUID,
    user_id: UUID,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    if action == "approve":
        return await service.approve_request(current_user.id, company_id, user_id)
    else:
        await service.reject_request(current_user.id, company_id, user_id)
        return {"detail": "Request rejected"}


@router.delete("/members/{user_id}")
async def remove_member_or_leave(
    company_id: UUID,
    user_id: UUID = None,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    if user_id:
        await service.remove_member(current_user.id, company_id, user_id)
        return {"detail": "Member removed"}
    else:
        await service.leave_company(current_user.id, company_id)
        return {"detail": "Left the company"}


@router.get("/invitations", response_model=list[CompanyMemberRead])
async def get_invitations(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_invitations(current_user.id)


@router.get("/requests", response_model=list[CompanyMemberRead])
async def get_requests(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_requests_for_owner(current_user.id, company_id)


@router.get("/members", response_model=list[CompanyMemberRead])
async def get_members(
    company_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    service: CompanyMembershipService = Depends(get_company_members_service),
):
    return await service.list_members(company_id, skip, limit)
