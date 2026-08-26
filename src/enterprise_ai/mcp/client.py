"""MCP client boundary for the Enterprise AI platform."""

from typing import Any

from mcp import Client

from enterprise_ai.mcp.capability_policy import (
    validate_tool_call,
)
from enterprise_ai.mcp.server import mcp_server


class MCPPlatformClient:
    """Thin application boundary around the MCP SDK client."""

    def __init__(self) -> None:
        """Initialize the MCP client against the platform server."""
        self._client = Client(mcp_server)

    async def __aenter__(self) -> "MCPPlatformClient":
        """Open the MCP client session."""
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> None:
        """Close the MCP client session."""
        await self._client.__aexit__(exc_type, exc_value, traceback)

    @property
    def server_info(self) -> Any:
        """Return negotiated server information."""
        return self._client.server_info

    @property
    def server_capabilities(self) -> Any:
        """Return negotiated server capabilities."""
        return self._client.server_capabilities

    @property
    def protocol_version(self) -> str:
        """Return the negotiated MCP protocol version."""
        value = self._client.protocol_version

        if not isinstance(value, str):
            raise TypeError("MCP protocol version must be a string.")

        return value

    async def list_tools(self) -> Any:
        """List tools exposed by the MCP server."""
        return await self._client.list_tools()

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """Validate and call an explicitly allowed MCP capability."""
        validate_tool_call(
            name,
            arguments,
        )

        return await self._client.call_tool(
            name,
            arguments=arguments,
        )

    async def list_resources(self) -> Any:
        """List resources exposed by the MCP server."""
        return await self._client.list_resources()

    async def read_resource(self, uri: str) -> Any:
        """Read an MCP resource."""
        return await self._client.read_resource(uri)

    async def list_prompts(self) -> Any:
        """List prompts exposed by the MCP server."""
        return await self._client.list_prompts()

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, str] | None = None,
    ) -> Any:
        """Render an MCP prompt."""
        return await self._client.get_prompt(
            name,
            arguments=arguments,
        )
