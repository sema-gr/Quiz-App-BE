from fastapi import HTTPException, status
import httpx
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.core.security import verify_password, create_access_token
from app.repository.user_repository import UserRepository
from app.schemas.user import Token, UserLogin
from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def login(self, credentials: UserLogin) -> Token:
        user = await self.repo.get_by_field("email", credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token({"sub": str(user.id)})
        return Token(access_token=token)

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

    async def login_auth0(self, token: str) -> User:
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
        if email is None:
            raise HTTPException(status_code=401, detail="Email claim missing in token")

        user = await self.repo.get_by_email(email)
        if user is None:
            user = await self.repo.create(
                User(email=email, full_name=email.split("@")[0], hashed_password="")
            )
        return user
