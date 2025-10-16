from uuid import UUID
from fastapi import HTTPException
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.models.company import Company


class CompanyService:
    def __init__(self, uow):
        self.uow = uow

    async def create_company(self, user_id: int, data: CompanyCreate):
        async with self.uow:
            company = Company(**data.dict(), owner_id=user_id)

            company = await self.uow.companies.create(company)
            return company

    async def update_company(self, user_id: int, company_id: int, data: CompanyUpdate):
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            if company.owner_id != user_id:
                raise HTTPException(status_code=403, detail="Permission denied")

            for key, value in data.dict(exclude_unset=True).items():
                setattr(company, key, value)
            await self.uow.commit()
            return company

    async def delete_company(self, user_id: UUID, company_id: UUID):
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            if company.owner_id != user_id:
                raise HTTPException(status_code=403, detail="Permission denied")

            await self.uow.companies.delete(company)
            await self.uow.commit()
            return {"detail": "Company deleted"}

    async def get_company(self, company_id: int):
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            return company

    async def list_companies(self, skip: int = 0, limit: int = 10):
        async with self.uow:
            return await self.uow.companies.list(skip=skip, limit=limit)

    async def change_visibility(self, user_id: int, company_id: int, visible: bool):
        async with self.uow:
            company = await self.uow.companies.get_by_field("id", company_id)
            if company.owner_id != user_id:
                raise HTTPException(403, "Not allowed")
            company.is_visible = visible
            await self.uow.commit()
            return company
