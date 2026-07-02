"""
VendorGuard AI application configuration.

This module loads environment settings and resolves filesystem paths
consistently regardless of the directory from which the backend is run.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/app/config.py
# parents[0] -> backend/app
# parents[1] -> backend
# parents[2] -> project root: vendorguard-ai-complete
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

    # These may be absolute paths or paths relative to the project root.
    db_path: str = Field(
        default="vendorguard.db",
        alias="DB_PATH",
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
            "http://127.0.0.1:5174"
        ),
        alias="CORS_ORIGINS",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    @staticmethod
    def _resolve_project_path(value: str) -> Path:
        """
        Resolve an absolute path directly, or resolve a relative path
        from the VendorGuard project root.
        """

        path = Path(value).expanduser()

        if path.is_absolute():
            return path.resolve()

        return (PROJECT_ROOT / path).resolve()

    @property
    def resolved_db_path(self) -> Path:
        """Absolute path of the SQLite database file."""

        return self._resolve_project_path(self.db_path)

    @property
    def resolved_sample_data_path(self) -> Path:
        """Absolute path of the synthetic vendor-data directory."""

        return self._resolve_project_path(self.sample_data_path)

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a clean list."""

        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Backward-compatible name used by older VendorGuard files.
        """

        return self.cors_origin_list


settings = Settings()