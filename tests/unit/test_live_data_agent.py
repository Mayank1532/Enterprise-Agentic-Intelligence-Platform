"""Tests for the Live Data ADK agent."""

from enterprise_ai.agents.adk.live_data_agent import (
    live_data_agent,
)
from enterprise_ai.agents.adk.mcp_tools import (
    mcp_live_data_tool,
)


def test_live_data_agent_has_expected_name() -> None:
    """Live Data Agent has the canonical agent name."""
    assert live_data_agent.name == "live_data_agent"


def test_live_data_agent_has_expected_model() -> None:
    """Live Data Agent uses the platform-approved ADK model."""
    assert live_data_agent.model == "gemini-2.5-flash"


def test_live_data_agent_exposes_live_data_tool() -> None:
    """Live Data Agent exposes the MCP-backed live-data tool."""
    assert mcp_live_data_tool in live_data_agent.tools


def test_live_data_agent_description_mentions_live_data() -> None:
    """Agent description identifies its live-data responsibility."""
    assert "live" in live_data_agent.description.lower()


def test_live_data_agent_instruction_prevents_fabrication() -> None:
    """Agent instructions explicitly prohibit fabricated live values."""
    instruction = live_data_agent.instruction.lower()

    assert "do not invent" in instruction
    assert "fabricat" in instruction
