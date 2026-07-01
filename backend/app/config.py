from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VendorGuard AI"
    environment: str = "development"
    db_path: str = "vendorguard.db"
    sample_data_path: str | None = None
    cors_origins: str = "http://localhost:5173"
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def resolved_sample_data_path(self) -> Path:
        if self.sample_data_path:
            return Path(self.sample_data_path).resolve()
        return Path(__file__).resolve().parents[2] / "sample_data"


settings = Settings()
