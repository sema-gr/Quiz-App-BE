from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str
    redis_url: str
    allowed_origins: List[str]

    @field_validator("allowed_origins", mode="before")
    def split_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip().strip('"') for origin in v.split(",")]
        return v


settings = Settings()
