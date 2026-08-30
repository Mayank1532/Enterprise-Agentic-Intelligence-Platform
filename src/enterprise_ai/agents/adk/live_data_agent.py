"""Google ADK Live Data Agent."""

from google.adk.agents import Agent

from enterprise_ai.agents.adk.mcp_tools import (
    mcp_live_data_tool,
)

live_data_agent = Agent(
    name="live_data_agent",
    model="gemini-2.5-flash",
    description=(
        "Retrieves current live external data through the "
        "platform MCP capability."
    ),
    instruction=(
        "You are the Live Data Agent. "
        "Use the mcp_live_data_tool when the user asks for "
        "current external live data. "
        "Do not invent live values. "
        "Use the returned source, timestamp, and value as the "
        "authoritative live evidence. "
        "If the live-data capability fails, clearly report the "
        "failure instead of fabricating an answer."
    ),
    tools=[
        mcp_live_data_tool,
    ],
)
