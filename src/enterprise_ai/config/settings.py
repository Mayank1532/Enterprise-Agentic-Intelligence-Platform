"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="enterprise-agentic-intelligence-platform",
        validation_alias="APP_NAME",
    )
    app_env: str = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )
    api_host: str = Field(
        default="0.0.0.0",
        validation_alias="API_HOST",
    )
    api_port: int = Field(
        default=8000,
        validation_alias="API_PORT",
    )

    llm_provider: str = Field(
        default="mock",
        validation_alias="LLM_PROVIDER",
    )
    llm_model: str = Field(
        default="",
        validation_alias="LLM_MODEL",
    )
    llm_base_url: str = Field(
        default="",
        validation_alias="LLM_BASE_URL",
    )
    llm_api_key: str = Field(
        default="",
        validation_alias="LLM_API_KEY",
    )

    api_auth_enabled: bool = Field(
        default=False,
        validation_alias="API_AUTH_ENABLED",
    )
    api_auth_key: str = Field(
        default="",
        validation_alias="API_AUTH_KEY",
    )
    api_rate_limit_requests: int = Field(
        default=60,
        validation_alias="API_RATE_LIMIT_REQUESTS",
    )
    api_rate_limit_window_seconds: int = Field(
        default=60,
        validation_alias="API_RATE_LIMIT_WINDOW_SECONDS",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
