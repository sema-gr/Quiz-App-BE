import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True, scope="session")
def fix_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield
    loop.close()


# @pytest.mark.asyncio
# async def test_create_user():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         response = await client.post("/users/", json={
#             "email": "snositel99@example.com",
#             "password": "secret123",
#             "full_name": "Sema"
#         })
#     assert response.status_code == 201


#  - docker compose exec backend poetry run pytest -v -s
@pytest.mark.asyncio
async def test_get_users():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users/")
        data = response.json()
        print(data)
        assert response.status_code == 200


# @pytest.mark.anyio
# async def test_update_user():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         user_id = "4d54b8d6-d9e8-49cd-a036-48a9521fb9e5"

#         update_resp = await client.put(f"/users/{user_id}", json={"full_name": "New Name"})
#         assert update_resp.status_code == 200
#         assert update_resp.json()["full_name"] == "New Name"


# @pytest.mark.asyncio
# async def test_delete_user():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as client:
#         user_id = "09ac01d9-992e-45cc-9ac8-c738b72de8f4"

#         delete_resp = await client.delete(f"/users/{user_id}")
#         assert delete_resp.status_code == 204

#         get_resp = await client.get(f"/users/{user_id}")
#         assert get_resp.status_code == 404
