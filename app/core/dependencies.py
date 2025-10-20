from app.db.postgres import async_session
from app.services.company_members_service import CompanyMembershipService
from app.services.company_service import CompanyService
from app.uow.unit_of_work import UnitOfWork
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_uow():
    return UnitOfWork(async_session)


async def get_current_user(
    token: str = Depends(oauth2_scheme), uow: UnitOfWork = Depends(get_uow)
):
    return await AuthService(uow).get_current_user(token)


def get_company_service(uow: UnitOfWork = Depends(get_uow)) -> CompanyService:
    return CompanyService(uow)


def get_company_members_service(
    uow: UnitOfWork = Depends(get_uow),
) -> CompanyMembershipService:
    return CompanyMembershipService(uow)
