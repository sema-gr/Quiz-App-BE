# import pytest
# from uuid import UUID
# from app.models.user import User
# from app.schemas.user import UserUpdate
# from app.services.user_service import UserService
# from app.core.security import verify_password


# @pytest.mark.asyncio
# async def test_update_existing_user_success(async_session):
#     service = UserService(async_session)

#     existing_user_id = UUID("88a412a4-138f-4511-8039-fdef02926f54")
#     current_user = await async_session.get(User, existing_user_id)

#     assert current_user is not None

#     update_data = UserUpdate(full_name="Tina", password="newpass123")
#     updated_user = await service.update(current_user.id, update_data, current_user)
#     await async_session.commit()

#     assert updated_user.full_name == "Tina"
#     assert verify_password("newpass123", updated_user.hashed_password)
