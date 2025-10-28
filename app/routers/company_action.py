from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_user, get_company_action_service
from app.models.user import User
from app.schemas.company import CompanyMemberRead
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
    return await service.manage_invitation(
        admin_id=current_user.id,
        company_id=company_id,
        target_user_id=user_id,
        action=action,
    )


@router.post("/invitations/response", response_model=CompanyMemberRead)
async def respond_invitation(
    company_id: UUID,
    action: str = Query(..., regex="^(accept|reject)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.respond_to_invitation(
        user_id=current_user.id, company_id=company_id, action_str=action
    )


@router.post("/requests", response_model=CompanyMemberRead)
async def create_join_request(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.manage_join_request(
        user_id=current_user.id, company_id=company_id, action="create"
    )


@router.post("/requests/{user_id}", response_model=CompanyMemberRead)
async def respond_join_request(
    company_id: UUID,
    user_id: UUID,
    action: str = Query(..., regex="^(accept|reject)$"),
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.respond_to_join_request(
        admin_id=current_user.id,
        company_id=company_id,
        target_user_id=user_id,
        action_str=action,
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


@router.post("/admins/{user_id}", response_model=CompanyMemberRead)
async def assign_admin(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.assign_admin(current_user.id, company_id, user_id)


@router.delete("/admins/{user_id}", response_model=CompanyMemberRead)
async def remove_admin(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.remove_admin(current_user.id, company_id, user_id)


@router.get("/admins", response_model=list[CompanyMemberRead])
async def list_admins(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyActionService = Depends(get_company_action_service),
):
    return await service.list_admins(company_id)
