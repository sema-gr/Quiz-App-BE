from fastapi import HTTPException, status
import httpx
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.core.security import hash_password, verify_password
from app.repository.user_repository import UserRepository
from app.schemas.user import Token, UserLogin, UserRegister
from app.models.user import User
from app.services.create_token import create_access_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def login(
        self, credentials: UserLogin | None = None, token: str | None = None
    ):
        if token:
            try:
                unverified_header = jwt.get_unverified_header(token)
                if "kid" in unverified_header:
                    return await self.login_auth0(token)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Local tokens are not used for login — please use email/password.",
                    )
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid token format")
        elif credentials:
            return await self.login_local(credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No credentials or token provided",
            )

    async def register(self, data: UserRegister) -> User:
        existing = await self.repo.get_by_field("email", data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        return await self.repo.create(user)

    async def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await self.repo.get_by_field("id", user_id)
        if user is None:
            raise credentials_exception

        return user

    async def login_local(self, credentials: UserLogin) -> Token:
        user = await self.repo.get_by_field("email", credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token({"sub": str(user.id)})
        return Token(access_token=token)

    async def login_auth0(self, token: str) -> Token:
        if not settings.auth0_domain or not settings.auth0_audience:
            raise HTTPException(status_code=500, detail="Auth0 not configured")

        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            r = await client.get(jwks_url)
            jwks = r.json()

        try:
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }
            if not rsa_key:
                raise HTTPException(status_code=401, detail="Invalid token header")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email claim missing in token")

        user = await self.repo.get_by_email(email)
        if not user:
            user = await self.repo.create(
                User(email=email, full_name=email.split("@")[0], hashed_password="")
            )

        token = create_access_token({"sub": str(user.id)})
        return Token(access_token=token)
