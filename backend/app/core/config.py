from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.db_url import normalize_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Duo API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str
    direct_url: str | None = None

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:3000"

    ai_provider: str = "openai"
    openai_api_key: str | None = None
    groq_api_key: str | None = None
    ai_model: str | None = None
    ai_base_url: str | None = None
    ai_enabled: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        """DATABASE_URL normalisée pour psycopg2 (runtime API + scripts)."""
        return normalize_database_url(self.database_url)

    @property
    def sqlalchemy_direct_url(self) -> str:
        """DIRECT_URL normalisée pour psycopg2 (migrations Alembic)."""
        return normalize_database_url(self.direct_url or self.database_url)

    @property
    def alembic_url(self) -> str:
        return self.sqlalchemy_direct_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
