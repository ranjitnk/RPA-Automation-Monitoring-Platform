"""Environment-based application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_name: str = "uipath-monitor-api"
    app_version: str = "1.0.0"
    app_log_level: str = "INFO"
    app_cors_origins: str = "http://localhost:5173"
    app_api_prefix: str = "/api/v1"

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://monitor:monitor@localhost:5432/uipath_monitor",
        alias="DATABASE_URL",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl_seconds: int = 300
    redis_enabled: bool = True

    # JWT
    jwt_secret_key: str = Field(
        default="dev-only-change-in-production-min-32-chars!!",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Elasticsearch
    es_enabled: bool = True
    es_url: str = "http://localhost:9200"
    es_username: str = "elastic"
    es_password: str = ""
    es_index_prefix: str = "uipath-monitor"
    es_verify_certs: bool = False

    # Scheduler
    scheduler_enabled: bool = True
    scheduler_sync_interval_seconds: int = 60
    scheduler_sla_interval_seconds: int = 120

    # Orchestrator defaults (per-env credentials stored in DB)
    orch_http_timeout_seconds: float = 60.0
    credentials_encryption_key: str = ""

    # Celery (optional distributed workers)
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_enabled: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.app_cors_origins.split(",") if o.strip()]

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("+asyncpg", "")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_in_production(cls, v: str, info) -> str:
        env = info.data.get("app_env", "development")
        if env == "production" and ("change" in v.lower() or "dev-only" in v.lower()):
            raise ValueError("JWT_SECRET_KEY must be a strong secret in production")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
