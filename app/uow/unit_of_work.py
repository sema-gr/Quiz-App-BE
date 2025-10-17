from app.uow.base import BaseUnitOfWork
from app.repository.company_repository import CompanyRepository


class UnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)
        self.companies: CompanyRepository | None = None

    async def __aenter__(self):
        await super().__aenter__()
        self.companies = CompanyRepository(self.session)
        return self
