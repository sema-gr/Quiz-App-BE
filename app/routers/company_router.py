from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_uow
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyRead
from app.services.company_service import CompanyService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyRead)
async def create_company(
    data: CompanyCreate,
    user=Depends(AuthService.get_current_user),
    uow=Depends(get_uow),
):
    return await CompanyService(uow).create_company(user.id, data)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int,
    data: CompanyUpdate,
    user=Depends(AuthService.get_current_user),
    uow=Depends(get_uow),
):
    return await CompanyService(uow).update_company(user.id, company_id, data)


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    user=Depends(AuthService.get_current_user),
    uow=Depends(get_uow),
):
    return await CompanyService(uow).delete_company(user.id, company_id)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, uow=Depends(get_uow)):
    return await CompanyService(uow).get_company(company_id)


@router.get("/", response_model=list[CompanyRead])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    uow=Depends(get_uow),
):
    return await CompanyService(uow).list_companies(skip, limit)


@router.patch("/{company_id}/visibility")
async def change_visibility(
    company_id: int,
    is_visible: bool,
    user=Depends(AuthService.get_current_user),
    uow=Depends(get_uow),
):
    return await CompanyService(uow).change_visibility(user.id, company_id, is_visible)
