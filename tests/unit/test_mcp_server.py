"""Tests for the MCP server foundation."""

from enterprise_ai.mcp.server import (
    create_mcp_server,
    mcp_server,
)


def test_mcp_server_can_be_created() -> None:
    """MCP server factory returns a server instance."""
    server = create_mcp_server()

    assert server is not None


def test_mcp_server_module_exposes_server() -> None:
    """Module exposes the platform MCP server."""
    assert mcp_server is not None
