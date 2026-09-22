from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    model_path: Path = Path("artifacts/nasih_model.joblib")
    store_backend: Literal["memory", "redis"] = "memory"
    redis_url: str | None = None

    @model_validator(mode="after")
    def validate_store_configuration(self) -> "Settings":
        if self.store_backend == "redis" and not self.redis_url:
            raise ValueError("REDIS_URL is required when STORE_BACKEND=redis")
        return self
