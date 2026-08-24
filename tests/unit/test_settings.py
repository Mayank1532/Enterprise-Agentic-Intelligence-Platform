"""Configuration tests."""

from enterprise_ai.config.settings import Settings


def test_default_settings() -> None:
    """Default configuration is safe for local development."""
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.llm_provider == "mock"
    assert settings.llm_api_key == ""
