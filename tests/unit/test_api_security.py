"""Tests for production API security controls."""

from fastapi.testclient import TestClient

from enterprise_ai.api.app import app
from enterprise_ai.api.security import FixedWindowRateLimiter
from enterprise_ai.config.settings import get_settings


def test_rate_limiter_allows_configured_requests() -> None:
    """Limiter allows requests up to the configured threshold."""
    limiter = FixedWindowRateLimiter(
        max_requests=2,
        window_seconds=60,
    )

    assert limiter.allow("client") is True
    assert limiter.allow("client") is True
    assert limiter.allow("client") is False


def test_rate_limiter_isolated_by_client() -> None:
    """Different clients have independent windows."""
    limiter = FixedWindowRateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False
    assert limiter.allow("client-b") is True


def test_rate_limiter_rejects_invalid_request_limit() -> None:
    """Invalid request limits are rejected."""
    try:
        FixedWindowRateLimiter(
            max_requests=0,
            window_seconds=60,
        )
    except ValueError as exc:
        assert "max_requests" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_rate_limiter_rejects_invalid_window() -> None:
    """Invalid windows are rejected."""
    try:
        FixedWindowRateLimiter(
            max_requests=1,
            window_seconds=0,
        )
    except ValueError as exc:
        assert "window_seconds" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_health_endpoint_remains_public(monkeypatch) -> None:
    """Health remains available without authentication."""
    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "test-secret-key")
    monkeypatch.setenv("API_RATE_LIMIT_REQUESTS", "1000")

    get_settings.cache_clear()

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    get_settings.cache_clear()


def test_ready_endpoint_remains_public(monkeypatch) -> None:
    """Readiness remains available without authentication."""
    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "test-secret-key")
    monkeypatch.setenv("API_RATE_LIMIT_REQUESTS", "1000")

    get_settings.cache_clear()

    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"

    get_settings.cache_clear()


def test_authentication_function_rejects_missing_key(monkeypatch) -> None:
    """Authentication rejects requests without an API key."""
    from fastapi import HTTPException, Request

    from enterprise_ai.api.security import authenticate_request

    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "test-secret-key")

    get_settings.cache_clear()

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/a2a",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
    }

    request = Request(scope)

    try:
        authenticate_request(request)
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Invalid or missing API key."
    else:
        raise AssertionError("Expected HTTPException.")

    get_settings.cache_clear()


def test_authentication_function_rejects_invalid_key(monkeypatch) -> None:
    """Authentication rejects requests with an incorrect API key."""
    from fastapi import HTTPException, Request

    from enterprise_ai.api.security import authenticate_request

    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "correct-secret-key")

    get_settings.cache_clear()

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/a2a",
        "headers": [(b"x-api-key", b"wrong-secret-key")],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
    }

    request = Request(scope)

    try:
        authenticate_request(request)
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Invalid or missing API key."
    else:
        raise AssertionError("Expected HTTPException.")

    get_settings.cache_clear()


def test_authentication_function_accepts_valid_key(monkeypatch) -> None:
    """Authentication accepts the configured API key."""
    from fastapi import Request

    from enterprise_ai.api.security import authenticate_request

    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "correct-secret-key")

    get_settings.cache_clear()

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/a2a",
        "headers": [(b"x-api-key", b"correct-secret-key")],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
    }

    request = Request(scope)

    authenticate_request(request)

    get_settings.cache_clear()


def test_authentication_function_without_key_fails_safely(monkeypatch) -> None:
    """Enabled authentication without a configured key fails safely."""
    from fastapi import HTTPException, Request

    from enterprise_ai.api.security import authenticate_request

    monkeypatch.setenv("API_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_AUTH_KEY", "")

    get_settings.cache_clear()

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/a2a",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
    }

    request = Request(scope)

    try:
        authenticate_request(request)
    except HTTPException as exc:
        assert exc.status_code == 503
        assert exc.detail == "API authentication is enabled but not configured."
    else:
        raise AssertionError("Expected HTTPException.")

    get_settings.cache_clear()


def test_rate_limit_function_returns_429(monkeypatch) -> None:
    """Rate limiting rejects requests above the configured threshold."""
    from fastapi import HTTPException, Request

    from enterprise_ai.api.security import enforce_rate_limit

    monkeypatch.setenv("API_AUTH_ENABLED", "false")
    monkeypatch.setenv("API_RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("API_RATE_LIMIT_WINDOW_SECONDS", "60")

    get_settings.cache_clear()

    class AppState:
        pass

    class TestApp:
        state = AppState()

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
        "app": TestApp,
    }

    request = Request(scope)
    request.app.state.rate_limiter = FixedWindowRateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    enforce_rate_limit(request)

    try:
        enforce_rate_limit(request)
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.detail == "Rate limit exceeded."
        assert exc.headers["Retry-After"] == "60"
    else:
        raise AssertionError("Expected HTTPException.")

    get_settings.cache_clear()
