"""Tests for the MCP client protocol boundary."""

import asyncio

from enterprise_ai.mcp.client import MCPPlatformClient


def test_mcp_client_negotiates_with_server() -> None:
    """Client establishes an MCP session with the platform server."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            assert client.server_info is not None
            assert client.server_info.name == "enterprise-ai"
            assert client.protocol_version

    asyncio.run(run())


def test_mcp_client_discovers_tool() -> None:
    """Client discovers the platform tool through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.list_tools()

            names = [tool.name for tool in result.tools]

            assert "platform_status" in names

    asyncio.run(run())


def test_mcp_client_calls_tool() -> None:
    """Client calls the platform tool through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.call_tool(
                "platform_status",
                arguments={},
            )

            assert result.is_error is False

            assert result.structured_content == {
                "platform": "enterprise-ai",
                "status": "operational",
                "execution_mode": "deterministic",
            }

    asyncio.run(run())


def test_mcp_client_discovers_resource() -> None:
    """Client discovers the platform resource through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.list_resources()

            uris = [resource.uri for resource in result.resources]

            assert "platform://status" in uris

    asyncio.run(run())


def test_mcp_client_reads_resource() -> None:
    """Client reads the platform resource through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.read_resource(
                "platform://status",
            )

            assert len(result.contents) == 1

            content = result.contents[0]

            assert content.text == (
                "platform=enterprise-ai\nstatus=operational\nexecution_mode=deterministic"
            )

    asyncio.run(run())


def test_mcp_client_discovers_prompt() -> None:
    """Client discovers the platform prompt through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.list_prompts()

            names = [prompt.name for prompt in result.prompts]

            assert "platform_analysis" in names

    asyncio.run(run())


def test_mcp_client_renders_prompt() -> None:
    """Client renders the platform prompt through MCP."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            result = await client.get_prompt(
                "platform_analysis",
                arguments={
                    "topic": "MCP architecture",
                },
            )

            assert len(result.messages) == 1
            assert result.messages[0].role == "user"
            assert result.messages[0].content.type == "text"

            assert "Topic: MCP architecture" in result.messages[0].content.text

    asyncio.run(run())


def test_mcp_client_exposes_expected_capabilities() -> None:
    """Negotiated server capabilities expose all three primitives."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            capabilities = client.server_capabilities

            assert capabilities is not None
            assert capabilities.tools is not None
            assert capabilities.resources is not None
            assert capabilities.prompts is not None

    asyncio.run(run())
