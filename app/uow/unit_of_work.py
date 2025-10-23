from app.repository.user import UserRepository
from app.uow.base import BaseUnitOfWork
from app.repository.company import CompanyRepository
from app.repository.company_members import CompanyMemberRepository


class UnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)
        self.users: UserRepository
        self.companies: CompanyRepository
        self.company_members: CompanyMemberRepository

    async def __aenter__(self):
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_members = CompanyMemberRepository(self.session)
        return self
