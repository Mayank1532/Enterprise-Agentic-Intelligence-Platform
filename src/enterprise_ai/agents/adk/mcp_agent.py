"""ADK foundation agent with an MCP-backed tool."""

from google.adk.agents import Agent

from enterprise_ai.agents.adk.mcp_tools import (
    mcp_platform_status_tool,
)


def create_mcp_enabled_agent() -> Agent:
    """Create an ADK agent whose tool boundary uses MCP."""
    return Agent(
        name="enterprise_mcp_agent",
        description=("ADK agent with a deterministic MCP-backed platform status capability."),
        instruction=(
            "You are an Enterprise AI platform agent. "
            "Use the platform status tool when platform status "
            "information is required. "
            "Do not invent platform status information."
        ),
        tools=[
            mcp_platform_status_tool,
        ],
    )


mcp_enabled_agent = create_mcp_enabled_agent()
