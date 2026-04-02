from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Transpop API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://transpop:transpop_dev@db:5432/transpop"
    database_url_sync: str = "postgresql+psycopg2://transpop:transpop_dev@db:5432/transpop"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # External services
    osrm_url: str = "http://osrm:5000"

    # Weather
    weather_api_key: str = ""
    weather_api_url: str = "https://api.openweathermap.org/data/2.5/forecast"


settings = Settings()
