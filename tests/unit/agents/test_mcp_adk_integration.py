"""Tests for MCP ↔ Google ADK integration."""

import asyncio

from google.adk.agents import Agent

from enterprise_ai.agents.adk.mcp_agent import (
    create_mcp_enabled_agent,
    mcp_enabled_agent,
)
from enterprise_ai.agents.adk.mcp_tools import (
    mcp_platform_status_tool,
)

EXPECTED_STATUS = {
    "platform": "enterprise-ai",
    "status": "operational",
    "execution_mode": "deterministic",
}


def test_mcp_backed_tool_is_async() -> None:
    """MCP-backed ADK tool is asynchronous."""
    assert asyncio.iscoroutinefunction(mcp_platform_status_tool)


def test_mcp_backed_tool_returns_mcp_result() -> None:
    """ADK-facing tool obtains its result through MCP."""

    async def run() -> None:
        result = await mcp_platform_status_tool()

        assert result == EXPECTED_STATUS

    asyncio.run(run())


def test_mcp_enabled_agent_is_adk_agent() -> None:
    """MCP-enabled integration produces an ADK Agent."""
    agent = create_mcp_enabled_agent()

    assert isinstance(agent, Agent)


def test_mcp_enabled_agent_identity() -> None:
    """MCP-enabled ADK agent has the canonical identity."""
    agent = create_mcp_enabled_agent()

    assert agent.name == "enterprise_mcp_agent"


def test_mcp_enabled_agent_has_tools() -> None:
    """ADK agent contains the MCP-backed tool."""
    agent = create_mcp_enabled_agent()

    assert agent.tools
    assert len(agent.tools) == 1


def test_global_mcp_enabled_agent_is_available() -> None:
    """Configured MCP-enabled agent is importable."""
    assert isinstance(mcp_enabled_agent, Agent)


def test_mcp_adapter_does_not_import_mcp_server() -> None:
    """Adapter depends on MCP client, not MCP server implementation."""
    import enterprise_ai.agents.adk.mcp_tools as module

    assert not hasattr(module, "mcp_server")
    assert "enterprise_ai.mcp.server" not in module.__dict__
