from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import (
    get_company_service,
    get_current_user,
    get_company_action_service,
)
from app.models.user import User
from app.schemas.company import CompanyMemberRead
from app.services.company import CompanyService
from app.services.company_action import CompanyActionService

router = APIRouter(prefix="/companies/{company_id}", tags=["Company Membership"])


@router.post("/invitations/{user_id}", response_model=CompanyMemberRead)
async def manage_invitation(
    company_id: UUID,
    user_id: UUID,
    action: str = Query(..., regex="^(invite|cancel)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.handle_action(
        user_id=current_user.id,
        company_id=company_id,
        target_user_id=user_id,
        action_type=action,
        role_check=True,
    )


@router.post("/invitations/accept-decline", response_model=CompanyMemberRead)
async def manage_invitation_response(
    company_id: UUID,
    action: str = Query(..., regex="^(accept|decline)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.handle_action(
        user_id=current_user.id,
        company_id=company_id,
        target_user_id=current_user.id,
        action_type=action,
    )


@router.post("/requests", response_model=CompanyMemberRead)
async def manage_join_request(
    company_id: UUID,
    action: str = Query(..., regex="^(create|cancel)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.handle_action(
        user_id=current_user.id,
        company_id=company_id,
        target_user_id=None,
        action_type=action,
    )


@router.post("/requests/{user_id}", response_model=CompanyMemberRead)
async def manage_request_approval(
    company_id: UUID,
    user_id: UUID,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.handle_action(
        user_id=current_user.id,
        company_id=company_id,
        target_user_id=user_id,
        action_type=action,
        role_check=True,
    )


@router.delete("/members/{user_id}", response_model=CompanyMemberRead)
async def remove_or_leave(
    company_id: UUID,
    user_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.remove_or_leave(
        user_id=current_user.id, company_id=company_id, target_user_id=user_id
    )


@router.get("/invitations", response_model=list[CompanyMemberRead])
async def list_invitations(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.list_invitations(current_user.id)


@router.get("/requests", response_model=list[CompanyMemberRead])
async def list_requests(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.list_requests_for_owner(current_user.id, company_id)


@router.get("/members", response_model=list[CompanyMemberRead])
async def list_members(
    company_id: UUID,
    skip: int = 0,
    limit: int = 10,
    service: CompanyService = Depends(get_company_service),
):
    return await service.list_members(company_id, skip, limit)
