"""Tests for MCP client capability enforcement."""

import asyncio

from enterprise_ai.mcp.capability_policy import MCPCapabilityError
from enterprise_ai.mcp.client import MCPPlatformClient


def test_client_allows_platform_status() -> None:
    """Client allows the canonical MCP capability."""

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


def test_client_denies_unknown_tool() -> None:
    """Client denies unknown capabilities before SDK execution."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            try:
                await client.call_tool(
                    "unknown_tool",
                    arguments={},
                )
            except MCPCapabilityError as exc:
                assert "not an allowed capability" in str(exc)
            else:
                raise AssertionError(
                    "Unknown MCP capability was not denied."
                )

    asyncio.run(run())


def test_client_denies_invalid_arguments() -> None:
    """Client denies invalid arguments before SDK execution."""

    async def run() -> None:
        async with MCPPlatformClient() as client:
            try:
                await client.call_tool(
                    "platform_status",
                    arguments={
                        "unexpected": "value",
                    },
                )
            except MCPCapabilityError as exc:
                assert "invalid arguments" in str(exc)
            else:
                raise AssertionError(
                    "Invalid MCP arguments were not denied."
                )

    asyncio.run(run())
