from app.core.exceptions import CompanyNotFound, PermissionDenied
from app.repository.user_repository import UserRepository
from app.uow.base import BaseUnitOfWork
from app.repository.company_repository import CompanyRepository
from app.repository.company_member_repository import CompanyMemberRepository


class UnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)
        self.users: UserRepository | None = None
        self.companies: CompanyRepository | None = None
        self.company_members: CompanyMemberRepository | None = None

    async def __aenter__(self):
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_members = CompanyMemberRepository(self.session)
        return self

    async def get_owned_company(self, owner_id, company_id):
        company = await self.companies.get_by_field("id", company_id)
        if not company:
            raise CompanyNotFound()
        if company.owner_id != owner_id:
            raise PermissionDenied()
        return company
