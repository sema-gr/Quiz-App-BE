from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies import get_auth_service
from app.services.auth import AuthService
from app.schemas.user import UserLogin, Token, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin | None = None,
    authorization: str | None = Header(default=None),
    service: AuthService = Depends(get_auth_service),
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        extracted = authorization.split(" ")[1]
        if extracted.strip():
            token = extracted

    return await service.login(credentials=user_login, token=token)


@router.get("/me", response_model=UserRead)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_current_user(token)
