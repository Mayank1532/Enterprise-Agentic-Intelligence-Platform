"""Tests for the ADK MCP tool boundary."""

import asyncio
from typing import Any

import pytest

from enterprise_ai.agents.adk.mcp_exceptions import MCPIntegrationError
from enterprise_ai.agents.adk.mcp_tools import (
    mcp_live_data_tool,
    mcp_platform_status_tool,
)


class FakeResult:
    """Minimal MCP call result used by deterministic tests."""

    def __init__(
        self,
        *,
        is_error: bool = False,
        structured_content: Any = None,
    ) -> None:
        self.is_error = is_error
        self.structured_content = structured_content


class FakeClient:
    """Minimal async MCP client used by deterministic tests."""

    def __init__(self) -> None:
        self.result: FakeResult | None = None
        self.error: Exception | None = None
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        return None

    async def call_tool(
        self,
        name: str,
        *,
        arguments: dict[str, Any],
    ) -> FakeResult:
        self.calls.append((name, arguments))

        if self.error is not None:
            raise self.error

        if self.result is None:
            raise RuntimeError("FakeClient result not configured.")

        return self.result


def test_live_data_tool_returns_structured_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live Data adapter returns MCP structured content unchanged."""

    expected = {
        "query": "Delhi",
        "value": "31.5 °C",
        "source_name": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
        "source_type": "live_external",
        "retrieved_at": "2026-08-30T00:00:00+00:00",
    }

    client = FakeClient()
    client.result = FakeResult(
        structured_content=expected,
    )

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    result = asyncio.run(
        mcp_live_data_tool("Delhi")
    )

    assert result == expected
    assert client.calls == [
        (
            "live_data",
            {
                "query": "Delhi",
            },
        )
    ]


def test_live_data_tool_rejects_mcp_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MCP error becomes an explicit integration error."""

    client = FakeClient()
    client.result = FakeResult(
        is_error=True,
        structured_content={
            "error": "provider failure",
        },
    )

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    with pytest.raises(
        MCPIntegrationError,
        match="MCP live data tool returned an error",
    ):
        asyncio.run(
            mcp_live_data_tool("Delhi")
        )


def test_live_data_tool_rejects_missing_structured_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing structured MCP content is rejected."""

    client = FakeClient()
    client.result = FakeResult(
        structured_content=None,
    )

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    with pytest.raises(
        MCPIntegrationError,
        match="no structured content",
    ):
        asyncio.run(
            mcp_live_data_tool("Delhi")
        )


def test_live_data_tool_rejects_non_mapping_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Non-dictionary structured content is rejected."""

    client = FakeClient()
    client.result = FakeResult(
        structured_content=[
            "unexpected",
        ],
    )

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    with pytest.raises(
        TypeError,
        match="must return a dictionary",
    ):
        asyncio.run(
            mcp_live_data_tool("Delhi")
        )


def test_live_data_tool_isolates_client_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Underlying MCP client failures are isolated explicitly."""

    client = FakeClient()
    client.error = RuntimeError("connection failure")

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    with pytest.raises(
        MCPIntegrationError,
        match="MCP live data operation failed",
    ):
        asyncio.run(
            mcp_live_data_tool("Delhi")
        )


def test_platform_status_adapter_remains_intact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing platform-status adapter remains functional."""

    expected = {
        "platform": "enterprise-ai",
        "status": "operational",
        "execution_mode": "deterministic",
    }

    client = FakeClient()
    client.result = FakeResult(
        structured_content=expected,
    )

    monkeypatch.setattr(
        "enterprise_ai.agents.adk.mcp_tools.MCPPlatformClient",
        lambda: client,
    )

    result = asyncio.run(
        mcp_platform_status_tool()
    )

    assert result == expected
    assert client.calls == [
        (
            "platform_status",
            {},
        )
    ]
