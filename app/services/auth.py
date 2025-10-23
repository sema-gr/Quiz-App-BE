import httpx
from jose import jwt, JWTError
from app.core.settings import settings
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    AuthConfigurationError,
    TokenValidationError,
)
from app.uow.unit_of_work import UnitOfWork
from app.schemas.user import Token, UserLogin, UserRegister
from app.models.user import User
from app.services.create_token import create_access_token


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def login(
        self, credentials: UserLogin | None = None, token: str | None = None
    ) -> Token:
        if token:
            try:
                unverified_header = jwt.get_unverified_header(token)
                if "kid" in unverified_header:
                    return await self.login_auth0(token)
                else:
                    raise InvalidTokenError(
                        "Local tokens are not used for login — please use email/password."
                    )
            except JWTError:
                raise InvalidTokenError("Invalid token format")
        elif credentials:
            return await self.login_local(credentials)
        else:
            raise InvalidCredentialsError("No credentials or token provided")

    async def register(self, data: UserRegister) -> User:
        async with self.uow:
            existing = await self.uow.users.get_by_field("email", data.email)
            if existing:
                raise UserAlreadyExistsError("User with this email already exists")

            user = User(
                email=data.email,
                full_name=data.full_name,
                hashed_password=hash_password(data.password),
            )

            user = await self.uow.users.create(user)
            await self.uow.session.flush()
            await self.uow.session.refresh(user)

            return user

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise TokenValidationError("User ID not found in token")
        except JWTError:
            raise TokenValidationError("Could not validate credentials")

        async with self.uow:
            user = await self.uow.users.get_by_field("id", user_id)
            if user is None:
                raise TokenValidationError("User not found")

            return user

    async def login_local(self, credentials: UserLogin) -> Token:
        async with self.uow:
            user = await self.uow.users.get_by_field("email", credentials.email)
            if not user or not verify_password(
                credentials.password, user.hashed_password
            ):
                raise InvalidCredentialsError("Invalid email or password")

            token = create_access_token({"sub": str(user.id)})
            return Token(access_token=token)

    async def _verify_auth0_token(self, token: str) -> dict:
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
                raise InvalidTokenError("Invalid token header")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
            return payload

        except JWTError:
            raise InvalidTokenError("Invalid token")

    async def login_auth0(self, token: str) -> Token:
        payload = await self._verify_auth0_token(token)

        email = payload.get("email")
        if not email:
            raise InvalidTokenError("Email claim missing in token")

        async with self.uow:
            user = await self.uow.users.get_by_field("email", email)
            if not user:
                user = User(
                    email=email, full_name=email.split("@")[0], hashed_password=""
                )
                user = await self.uow.users.create(user)
                await self.uow.session.flush()
                await self.uow.session.refresh(user)

            token = create_access_token({"sub": str(user.id)})
            return Token(access_token=token)
