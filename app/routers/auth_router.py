from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin, Token, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserRead, status_code=201)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin | None = None,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    token = None
    if authorization and authorization.startswith("Bearer "):
        extracted = authorization.split(" ")[1]
        if extracted.strip():
            token = extracted

    return await service.login(credentials=user_login, token=token)


@router.get("/me", response_model=UserRead)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.get_current_user(token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await AuthService(db).get_current_user(token)
