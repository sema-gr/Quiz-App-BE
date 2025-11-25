# import pytest
# from uuid import uuid4
# import pytest_asyncio
# from main import app
# from app.core.database import get_db
# from app.models.company import Company
# from app.models.user import User
# from app.schemas.company import CompanyCreate, CompanyUpdate
# from app.services.company import CompanyService
# from app.uow.unit_of_work import UnitOfWork


# @pytest_asyncio.fixture(autouse=True)
# async def override_get_db(async_session):
#     async def _override():
#         async with async_session as session:
#             yield session

#     app.dependency_overrides[get_db] = _override
#     yield
#     app.dependency_overrides[get_db] = get_db


# @pytest.mark.asyncio
# async def test_create_company(async_session):
#     user = User(
#         id=uuid4(),
#         email="test@example.com",
#         full_name="Test User",
#         hashed_password="hashedpass123",
#     )
#     async_session.add(user)
#     await async_session.commit()

#     uow = UnitOfWork(lambda: async_session)
#     service = CompanyService(uow)

#     data = CompanyCreate(name="Test Company", description="This is a test company")

#     company = await service.create_company(user.id, data)
#     await async_session.commit()

#     assert company.name == "Test Company"
#     assert company.owner_id == user.id


# @pytest.mark.asyncio
# async def test_get_company(async_session):
#     uow = UnitOfWork(lambda: async_session)
#     service = CompanyService(uow)

#     owner_id = uuid4()
#     user = User(
#         id=owner_id,
#         email="owner@example.com",
#         full_name="Owner User",
#         hashed_password="hashedpass123",
#     )
#     async_session.add(user)
#     await async_session.commit()

#     company = Company(
#         id=uuid4(),
#         name="GetCo",
#         description="Company to get",
#         is_visible=True,
#         owner_id=owner_id,
#     )
#     async_session.add(company)
#     await async_session.commit()

#     result = await service.get_company(company.id)
#     assert result is not None
#     assert result.name == "GetCo"


# @pytest.mark.asyncio
# async def test_update_company(async_session):
#     uow = UnitOfWork(lambda: async_session)
#     service = CompanyService(uow)

#     owner_id = uuid4()
#     user = User(
#         id=owner_id,
#         email="owner@example.com",
#         full_name="Owner User",
#         hashed_password="hashedpass123",
#     )
#     async_session.add(user)
#     await async_session.commit()

#     company = Company(
#         id=uuid4(),
#         name="OldName",
#         description="Old desc",
#         is_visible=True,
#         owner_id=owner_id,
#     )
#     async_session.add(company)
#     await async_session.commit()

#     update_data = CompanyUpdate(name="NewName", description="Updated desc")
#     updated = await service.update_company(owner_id, company.id, update_data)
#     await async_session.commit()

#     assert updated.name == "NewName"
#     assert updated.description == "Updated desc"


# @pytest.mark.asyncio
# async def test_change_visibility(async_session):
#     uow = UnitOfWork(lambda: async_session)
#     service = CompanyService(uow)

#     owner_id = uuid4()
#     user = User(
#         id=owner_id,
#         email="owner@example.com",
#         full_name="Owner User",
#         hashed_password="hashedpass123",
#     )
#     async_session.add(user)
#     await async_session.commit()

#     company = Company(
#         id=uuid4(),
#         name="VisibleCo",
#         description="Should change visibility",
#         is_visible=True,
#         owner_id=owner_id,
#     )
#     async_session.add(company)
#     await async_session.commit()

#     updated = await service.change_visibility(owner_id, company.id, False)
#     await async_session.commit()

#     assert updated.is_visible is False


# @pytest.mark.asyncio
# async def test_delete_company(async_session):
#     uow = UnitOfWork(lambda: async_session)
#     service = CompanyService(uow)
#     owner_id = uuid4()

#     user = User(
#         id=owner_id,
#         email="owner@example.com",
#         full_name="Owner User",
#         hashed_password="hashedpass123",
#     )
#     async_session.add(user)
#     await async_session.commit()

#     company = Company(
#         id=uuid4(),
#         name="DeleteMe",
#         description="Company to delete",
#         is_visible=True,
#         owner_id=owner_id,
#     )
#     async_session.add(company)
#     await async_session.commit()

#     response = await service.delete_company(owner_id, company.id)
#     await async_session.commit()

#     assert response["detail"] == "Company deleted"
#     deleted = await async_session.get(Company, company.id)
#     assert deleted is None
