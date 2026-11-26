from functools import lru_cache
from typing import Literal
from pydantic import SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from BIZOPS_* environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BIZOPS_", extra="ignore")

    database_url: SecretStr | None = None
    migration_database_url: SecretStr | None = None
    app_name: str = "BizOps AI Worker"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()