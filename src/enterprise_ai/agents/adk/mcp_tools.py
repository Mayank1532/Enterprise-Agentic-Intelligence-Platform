"""MCP-backed tools exposed through the Google ADK boundary."""

from typing import Any

from enterprise_ai.mcp.client import MCPPlatformClient


async def mcp_platform_status_tool() -> dict[str, Any]:
    """Return platform status through the MCP client boundary.

    This function is intentionally async because the underlying MCP
    protocol is asynchronous.

    The ADK agent receives this function as a normal function tool.
    The function itself knows nothing about the MCP server
    implementation; it depends only on MCPPlatformClient.
    """
    async with MCPPlatformClient() as client:
        result = await client.call_tool(
            "platform_status",
            arguments={},
        )

    if result.is_error:
        raise RuntimeError("MCP platform_status tool returned an error.")

    if result.structured_content is None:
        raise RuntimeError("MCP platform_status tool returned no structured content.")

    if not isinstance(result.structured_content, dict):
        raise TypeError("MCP platform_status tool must return a dictionary.")

    return result.structured_content
