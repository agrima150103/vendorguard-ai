"""
VendorGuard AI application configuration.

Supports local SQLite development and PostgreSQL/Supabase production through
one DATABASE_URL setting.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="VendorGuard AI",
        alias="APP_NAME",
    )

    gemini_api_key: str = Field(
        default="",
        alias="GEMINI_API_KEY",
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash-lite",
        alias="GEMINI_MODEL",
    )

    db_path: str = Field(
        default="vendorguard.db",
        alias="DB_PATH",
    )

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
    )

    sample_data_path: str = Field(
        default="sample_data",
        alias="SAMPLE_DATA_PATH",
    )

    cors_origins: str = Field(
        default=(
            "http://localhost:5173,"
            "http://127.0.0.1:5173,"
            "http://localhost:5174,"
            "http://127.0.0.1:5174,"
            "http://localhost:4173,"
            "http://127.0.0.1:4173"
        ),
        alias="CORS_ORIGINS",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    @staticmethod
    def _resolve_project_path(value: str) -> Path:
        """Resolve absolute paths directly and relative paths from project root."""

        path = Path(value).expanduser()

        if path.is_absolute():
            return path.resolve()

        return (PROJECT_ROOT / path).resolve()

    @property
    def resolved_db_path(self) -> Path:
        """Absolute path of the local SQLite database file."""

        return self._resolve_project_path(self.db_path)

    @property
    def resolved_sample_data_path(self) -> Path:
        """Absolute path of the synthetic vendor-data directory."""

        return self._resolve_project_path(self.sample_data_path)

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a cleaned list."""

        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def cors_origins_list(self) -> list[str]:
        """Backward-compatible alias used by older files."""

        return self.cors_origin_list

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Return a SQLAlchemy-compatible database URL.

        Local default:
            sqlite:///...

        Production Supabase:
            postgresql+psycopg://...
        """

        raw_url = self.database_url.strip()

        if not raw_url:
            return f"sqlite:///{self.resolved_db_path.as_posix()}"

        if raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )

        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1,
            )

        if (
            raw_url.startswith("postgresql+psycopg://")
            and "sslmode=" not in raw_url
        ):
            separator = "&" if "?" in raw_url else "?"
            raw_url = f"{raw_url}{separator}sslmode=require"

        return raw_url

    @property
    def using_postgres(self) -> bool:
        """Return True when the configured database is PostgreSQL."""

        return self.sqlalchemy_database_url.startswith(
            "postgresql+psycopg://"
        )


settings = Settings()