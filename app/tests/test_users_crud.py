import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.database import get_db


@pytest_asyncio.fixture(autouse=True)
async def override_get_db(async_session):
    async def _override():
        async with async_session as session:
            yield session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides[get_db] = get_db


@pytest.mark.asyncio
async def test_get_users():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        print("Users in test DB:", data)
        assert isinstance(data, list)


# @pytest.mark.asyncio
# async def test_create_user():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.post(
#             "/users/",
#             json={
#                 "email": "snositel99@example.com",
#                 "password": "secret123",
#                 "full_name": "Sema",
#             },
#         )
#         assert response.status_code == 201
#         data = response.json()
#         assert data["email"] == "snositel99@example.com"
#         assert data["full_name"] == "Sema"

# @pytest.mark.asyncio
# async def test_update_user():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         # Спочатку створимо юзера
#         response = await client.post(
#             "/users/",
#             json={
#                 "email": "update@example.com",
#                 "password": "pass123",
#                 "full_name": "OldName",
#             },
#         )
#         user_id = response.json()["id"]

#         # Оновимо дані
#         response = await client.put(
#             f"/users/{user_id}",
#             json={
#                 "full_name": "NewName",
#                 "password": "newpass123"
#             }
#         )
#         assert response.status_code == 200
#         data = response.json()
#         assert data["full_name"] == "NewName"

# @pytest.mark.asyncio
# async def test_delete_user():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         # Спочатку створимо юзера
#         response = await client.post(
#             "/users/",
#             json={
#                 "email": "delete@example.com",
#                 "password": "pass123",
#                 "full_name": "ToDelete",
#             },
#         )
#         user_id = response.json()["id"]

#         # Видалимо
#         response = await client.delete(f"/users/{user_id}")
#         assert response.status_code == 204

#         # Перевіримо, що його більше немає
#         response = await client.get("/users/")
#         data = response.json()
#         assert all(u["id"] != user_id for u in data)
