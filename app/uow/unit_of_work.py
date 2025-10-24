from app.repository.user import UserRepository
from app.repository.company import CompanyRepository
from app.repository.company_action import CompanyActionRepository
from app.repository.company_association import CompanyAssociationRepository
from app.uow.base import BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)
        self.users: UserRepository
        self.companies: CompanyRepository
        self.company_actions: CompanyActionRepository
        self.company_associations: CompanyAssociationRepository

    async def __aenter__(self):
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_actions = CompanyActionRepository(self.session)
        self.company_associations = CompanyAssociationRepository(self.session)
        return self
