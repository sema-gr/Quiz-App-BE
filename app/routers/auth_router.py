from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin, Token, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(user_login)


@router.get("/me", response_model=UserRead)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.get_current_user(token)


@router.get("/auth0", response_model=UserRead)
async def auth0_login(
    authorization: str = Header(...), db: AsyncSession = Depends(get_db)
):
    token = authorization.split(" ")[1]
    service = AuthService(db)
    return await service.login_auth0(token)
