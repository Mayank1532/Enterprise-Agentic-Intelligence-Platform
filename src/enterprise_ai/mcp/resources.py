"""Deterministic MCP resources for the Enterprise AI platform."""

from mcp.server import MCPServer

PLATFORM_STATUS_RESOURCE_URI = "platform://status"


def get_platform_status_resource() -> str:
    """Return deterministic platform status resource content."""
    return "platform=enterprise-ai\nstatus=operational\nexecution_mode=deterministic"


def register_resources(server: MCPServer) -> None:
    """Register platform resources on the supplied MCP server."""

    @server.resource(PLATFORM_STATUS_RESOURCE_URI)
    def platform_status_resource() -> str:
        """Expose deterministic platform status."""
        return get_platform_status_resource()
