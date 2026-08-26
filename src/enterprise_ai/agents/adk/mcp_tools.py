"""MCP-backed tools exposed through the Google ADK boundary."""

from typing import Any

from enterprise_ai.agents.adk.mcp_exceptions import (
    MCPIntegrationError,
)
from enterprise_ai.mcp.client import MCPPlatformClient


async def mcp_platform_status_tool() -> dict[str, Any]:
    """Return platform status through the MCP client boundary.

    MCP failures are deliberately converted into an explicit
    integration error. No fallback value is returned because
    doing so could cause the ADK layer to operate on fabricated
    platform state.
    """
    try:
        async with MCPPlatformClient() as client:
            result = await client.call_tool(
                "platform_status",
                arguments={},
            )
    except Exception as exc:
        raise MCPIntegrationError("MCP platform status operation failed.") from exc

    if result.is_error:
        raise MCPIntegrationError("MCP platform status tool returned an error.")

    if result.structured_content is None:
        raise MCPIntegrationError("MCP platform status tool returned no structured content.")

    if not isinstance(result.structured_content, dict):
        raise TypeError("MCP platform status tool must return a dictionary.")

    return result.structured_content
