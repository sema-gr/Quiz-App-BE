import pytest
from uuid import uuid4
import pytest_asyncio
from app.models.company_association import CompanyAssociation
from app.services.company_action import CompanyActionService
from main import app
from app.core.database import get_db
from app.uow.unit_of_work import UnitOfWork


@pytest_asyncio.fixture(autouse=True)
async def override_get_db(async_session):
    async def _override():
        async with async_session as session:
            yield session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides[get_db] = get_db


@pytest.mark.asyncio
async def test_assign_admin(async_session):
    uow = UnitOfWork(async_session)
    service = CompanyActionService(uow)

    owner_id = uuid4()
    user_id = uuid4()
    company_id = uuid4()

    assoc = CompanyAssociation(user_id=user_id, company_id=company_id, role="member")
    async_session.add(assoc)
    await async_session.commit()

    updated = await service.assign_admin(owner_id, company_id, user_id)
    await async_session.commit()

    assert updated.role == "admin"
