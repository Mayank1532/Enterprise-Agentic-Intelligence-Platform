"""Tests for deterministic MCP tools."""

from enterprise_ai.mcp.server import (
    create_mcp_server,
    mcp_server,
)
from enterprise_ai.mcp.tools import get_platform_status


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
