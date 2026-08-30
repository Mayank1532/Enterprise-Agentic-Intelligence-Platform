"""Deterministic MCP tools for the Enterprise AI platform."""

from typing import Any

from mcp.server import MCPServer

from enterprise_ai.common.live_data_client import PublicLiveDataProvider
from enterprise_ai.core.live_data import LiveData


def get_platform_status() -> dict[str, Any]:
    """Return deterministic platform status information."""
    return {
        "platform": "enterprise-ai",
        "status": "operational",
        "execution_mode": "deterministic",
    }


async def get_live_data(query: str) -> LiveData:
    """Retrieve normalized live data for a supported location."""
    provider = PublicLiveDataProvider()
    return await provider.fetch(query)


def register_tools(server: MCPServer) -> None:
    """Register platform tools on the supplied MCP server."""

    @server.tool()
    def platform_status() -> dict[str, Any]:
        """Return deterministic platform status information."""
        return get_platform_status()

    @server.tool()
    async def live_data(query: str) -> LiveData:
        """Retrieve live external data for a supported location."""
        return await get_live_data(query)
