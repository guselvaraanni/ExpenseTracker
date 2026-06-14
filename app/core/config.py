"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Expense Tracker"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/expense_tracker"
    )

    # Security
    secret_key: str = "change-me-to-a-long-random-secret-key"

    # Session
    session_cookie_name: str = "expense_tracker_session"
    session_max_age: int = 86400  # 24 hours

    # Logging
    log_level: str = "INFO"

    @property
    def templates_dir(self) -> Path:
        return APP_DIR / "templates"

    @property
    def static_dir(self) -> Path:
        return APP_DIR / "static"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
