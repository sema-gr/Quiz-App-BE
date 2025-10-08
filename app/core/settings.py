from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str
    redis_url: str
    allowed_origins: List[str]

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    auth0_domain: str | None = None
    auth0_audience: str | None = None
    auth0_issuer: str | None = None


settings = Settings()
