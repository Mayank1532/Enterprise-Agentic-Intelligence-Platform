"""Tests for deterministic MCP tools."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import HttpUrl

from enterprise_ai.core.live_data import LiveData
from enterprise_ai.mcp.server import (
    create_mcp_server,
    mcp_server,
)
from enterprise_ai.mcp.tools import (
    get_live_data,
    get_platform_status,
)


def test_get_platform_status_is_deterministic() -> None:
    """Platform status returns the same result every time."""
    first = get_platform_status()
    second = get_platform_status()

    assert first == second


def test_get_platform_status_contract() -> None:
    """Platform status exposes the canonical fields."""
    result = get_platform_status()

    assert result == {
        "platform": "enterprise-ai",
        "status": "operational",
        "execution_mode": "deterministic",
    }


def test_mcp_server_can_be_created() -> None:
    """MCP server factory returns a configured server."""
    server = create_mcp_server()

    assert server is not None


def test_global_mcp_server_is_available() -> None:
    """Module exposes the configured MCP server."""
    assert mcp_server is not None


def test_get_live_data_returns_normalized_live_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MCP-facing live-data function preserves the provider contract."""

    expected = LiveData(
        query="Delhi",
        value="31.5 °C",
        source_name="Open-Meteo",
        source_url=HttpUrl("https://open-meteo.com/"),
        retrieved_at=datetime.now(UTC),
    )

    class MockProvider:
        async def fetch(self, query: str) -> LiveData:
            assert query == "Delhi"
            return expected

    monkeypatch.setattr(
        "enterprise_ai.mcp.tools.PublicLiveDataProvider",
        MockProvider,
    )

    result = asyncio.run(get_live_data("Delhi"))

    assert result == expected
    assert result.source_type == "live_external"
    assert result.source_name == "Open-Meteo"


def test_get_live_data_propagates_provider_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MCP-facing live-data function does not hide provider errors."""

    class MockProvider:
        async def fetch(self, query: str) -> LiveData:
            raise ValueError(
                f"Unsupported live-data location: {query}"
            )

    monkeypatch.setattr(
        "enterprise_ai.mcp.tools.PublicLiveDataProvider",
        MockProvider,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported live-data location",
    ):
        asyncio.run(get_live_data("Paris"))


def test_live_data_tool_is_registered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MCP registration includes the live-data capability."""

    registered: list[str] = []

    class FakeServer:
        def tool(self) -> Any:
            def decorator(function: Any) -> Any:
                registered.append(function.__name__)
                return function

            return decorator

    from enterprise_ai.mcp.tools import register_tools

    register_tools(FakeServer())

    assert registered == [
        "platform_status",
        "live_data",
    ]
