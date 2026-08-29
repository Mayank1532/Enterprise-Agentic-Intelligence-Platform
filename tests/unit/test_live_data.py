"""Tests for the provider-neutral live data contract."""

import asyncio
from datetime import UTC, datetime

import httpx
import pytest
from pydantic import ValidationError

from enterprise_ai.common.live_data_client import PublicLiveDataProvider
from enterprise_ai.core.live_data import LiveData


def test_live_data_preserves_source_metadata() -> None:
    """Live data preserves external source provenance."""
    data = LiveData(
        query="weather",
        value="20 C",
        source_name="Open-Meteo",
        source_url="https://open-meteo.com/",
        retrieved_at=datetime.now(UTC),
    )

    assert data.query == "weather"
    assert data.value == "20 C"
    assert data.source_name == "Open-Meteo"
    assert str(data.source_url).startswith("https://open-meteo.com/")
    assert data.source_type == "live_external"


def test_live_data_requires_timezone_aware_timestamp() -> None:
    """Live data accepts explicit retrieval timestamps."""
    timestamp = datetime.now(UTC)

    data = LiveData(
        query="status",
        value="operational",
        source_name="test-provider",
        source_url="https://example.com/data",
        retrieved_at=timestamp,
    )

    assert data.retrieved_at == timestamp
    assert data.is_fresh


def test_live_data_rejects_empty_query() -> None:
    """Empty live-data queries are rejected."""
    with pytest.raises(ValidationError):
        LiveData(
            query="",
            value="value",
            source_name="provider",
            source_url="https://example.com/data",
            retrieved_at=datetime.now(UTC),
        )


def test_live_data_rejects_empty_value() -> None:
    """Empty live-data values are rejected."""
    with pytest.raises(ValidationError):
        LiveData(
            query="query",
            value="",
            source_name="provider",
            source_url="https://example.com/data",
            retrieved_at=datetime.now(UTC),
        )


def test_live_data_factory_uses_utc() -> None:
    """Factory creates timezone-aware UTC retrieval timestamps."""
    data = LiveData.create(
        query="status",
        value="operational",
        source_name="provider",
        source_url="https://example.com/data",
    )

    assert data.retrieved_at.tzinfo is not None
    assert data.retrieved_at.utcoffset() == UTC.utcoffset(
        data.retrieved_at
    )


def test_provider_returns_normalized_live_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider normalizes a valid external response."""

    class MockResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "current": {
                    "temperature_2m": 31.5,
                },
                "current_units": {
                    "temperature_2m": "°C",
                },
            }

    class MockClient:
        async def __aenter__(self) -> "MockClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object,
        ) -> None:
            return None

        async def get(
            self,
            url: str,
            *,
            params: dict[str, object],
        ) -> MockResponse:
            assert url == PublicLiveDataProvider.BASE_URL
            assert params["latitude"] == 28.6139
            assert params["longitude"] == 77.2090
            assert params["current"] == "temperature_2m"
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(),
    )

    result = asyncio.run(
        PublicLiveDataProvider().fetch("Delhi")
    )

    assert result.query == "Delhi"
    assert result.value == "31.5 °C"
    assert result.source_name == "Open-Meteo"
    assert result.source_type == "live_external"
    assert result.retrieved_at.tzinfo is not None


def test_provider_rejects_empty_query() -> None:
    """Provider rejects an empty location query."""

    async def run() -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            await PublicLiveDataProvider().fetch("   ")

    asyncio.run(run())


def test_provider_rejects_unsupported_location() -> None:
    """Provider rejects locations outside the Phase 6 scope."""

    async def run() -> None:
        with pytest.raises(
            ValueError,
            match="Unsupported live-data location",
        ):
            await PublicLiveDataProvider().fetch("Paris")

    asyncio.run(run())


def test_provider_converts_http_failure_to_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider exposes external HTTP failure explicitly."""

    class MockClient:
        async def __aenter__(self) -> "MockClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object,
        ) -> None:
            return None

        async def get(
            self,
            url: str,
            *,
            params: dict[str, object],
        ) -> httpx.Response:
            request = httpx.Request("GET", url)

            return httpx.Response(
                503,
                request=request,
            )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(),
    )

    async def run() -> None:
        with pytest.raises(
            RuntimeError,
            match="Live data provider request failed",
        ):
            await PublicLiveDataProvider().fetch("Delhi")

    asyncio.run(run())


def test_provider_rejects_malformed_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider rejects malformed external payloads."""

    class MockResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "unexpected": "payload",
            }

    class MockClient:
        async def __aenter__(self) -> "MockClient":
            return self

        async def __aexit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object,
        ) -> None:
            return None

        async def get(
            self,
            url: str,
            *,
            params: dict[str, object],
        ) -> MockResponse:
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(),
    )

    async def run() -> None:
        with pytest.raises(
            RuntimeError,
            match="invalid response",
        ):
            await PublicLiveDataProvider().fetch("Delhi")

    asyncio.run(run())
