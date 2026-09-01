"""Lightweight production API security controls."""

from __future__ import annotations

from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status

from enterprise_ai.config.settings import get_settings


class FixedWindowRateLimiter:
    """Process-local fixed-window request limiter."""

    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than zero.")

        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero.")

        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._lock = Lock()
        self._windows: dict[str, tuple[float, int]] = {}

    def allow(self, key: str) -> bool:
        """Return whether the request is within the configured limit."""
        now = monotonic()

        with self._lock:
            window = self._windows.get(key)

            if window is None:
                self._windows[key] = (now, 1)
                return True

            started_at, count = window

            if now - started_at >= self._window_seconds:
                self._windows[key] = (now, 1)
                return True

            if count >= self._max_requests:
                return False

            self._windows[key] = (started_at, count + 1)
            return True


def _client_key(request: Request) -> str:
    """Return the ASGI client address used for rate limiting."""
    if request.client is not None:
        return request.client.host

    return "unknown"


def authenticate_request(request: Request) -> None:
    """Validate the configured API key when authentication is enabled."""
    settings = get_settings()

    if not settings.api_auth_enabled:
        return

    if not settings.api_auth_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is enabled but not configured.",
        )

    supplied_key = request.headers.get("X-API-Key")

    if supplied_key != settings.api_auth_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


def enforce_rate_limit(request: Request) -> None:
    """Apply the configured process-local API rate limit."""
    settings = get_settings()

    limiter = getattr(request.app.state, "rate_limiter", None)

    if limiter is None:
        limiter = FixedWindowRateLimiter(
            max_requests=settings.api_rate_limit_requests,
            window_seconds=settings.api_rate_limit_window_seconds,
        )
        request.app.state.rate_limiter = limiter

    if not limiter.allow(_client_key(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
            headers={"Retry-After": str(settings.api_rate_limit_window_seconds)},
        )
