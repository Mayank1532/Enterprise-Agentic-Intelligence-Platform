"""Deterministic MCP tools for the Enterprise AI platform."""

from typing import Any

from mcp.server import MCPServer


def get_platform_status() -> dict[str, Any]:
    """Return deterministic platform status information."""
    return {
        "platform": "enterprise-ai",
        "status": "operational",
        "execution_mode": "deterministic",
    }


def register_tools(server: MCPServer) -> None:
    """Register platform tools on the supplied MCP server."""

    @server.tool()
    def platform_status() -> dict[str, Any]:
        """Return deterministic platform status information."""
        return get_platform_status()
