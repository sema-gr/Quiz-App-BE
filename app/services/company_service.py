from uuid import UUID
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.models.company import Company
from app.core.exceptions import CompanyNotFound, PermissionDenied
from app.uow.unit_of_work import UnitOfWork


class CompanyService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_company(self, user_id: UUID, data: CompanyCreate) -> Company:
        async with self.uow:
            company_data = data.dict()
            company_data["owner_id"] = user_id

            company = Company(**company_data)
            result = await self.uow.companies.create(company)
            return result

    async def update_company(
        self, user_id: UUID, company_id: UUID, data: CompanyUpdate
    ) -> Company:
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise CompanyNotFound()
            if company.owner_id != user_id:
                raise PermissionDenied()

            for field, value in data.dict(exclude_unset=True).items():
                setattr(company, field, value)

            return await self.uow.companies.update(company)

    async def delete_company(self, user_id: UUID, company_id: UUID) -> Company:
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise CompanyNotFound()
            if company.owner_id != user_id:
                raise PermissionDenied()

            await self.uow.companies.delete(company)
            return company

    async def get_company(self, company_id: UUID) -> Company:
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise CompanyNotFound()
            return company

    async def list_companies(self, skip: int = 0, limit: int = 10) -> list[Company]:
        async with self.uow:
            return await self.uow.companies.get_all(skip=skip, limit=limit)

    async def change_visibility(
        self, user_id: UUID, company_id: UUID, visible: bool
    ) -> Company:
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise CompanyNotFound()
            if company.owner_id != user_id:
                raise PermissionDenied()

            company.is_visible = visible
            return await self.uow.companies.update(company)
