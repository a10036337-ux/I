from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Taiwan Quant Trading System"
    database_url: str = "sqlite:///./database/trading.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    shioaji_simulation: bool = True
    shioaji_api_key: str | None = None
    shioaji_secret_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.removeprefix("sqlite:///"))
        return Path("database/trading.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()
