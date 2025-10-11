import pytest
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user_service import UserService
from uuid import uuid4


@pytest.mark.anyio
async def test_update_own_profile_success(async_session):
    service = UserService(async_session)
    current_user = User(
        id=uuid4(),
        email="alkogolik.show@gmail.com",
        full_name="Sema",
        hashed_password="12345678",
    )

    async_session.add(current_user)
    await async_session.flush()

    update_data = UserUpdate(full_name="Anna", password="newpass123")
    updated_user = await service.update(current_user.id, update_data, current_user)

    assert updated_user.full_name == "Anna"
    assert updated_user.hashed_password != "12345678"
