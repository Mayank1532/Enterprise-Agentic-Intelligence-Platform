"""Tests for the Google ADK foundation agent."""

from google.adk.agents import Agent

from enterprise_ai.agents.adk.foundation_agent import (
    create_foundation_agent,
)


def test_foundation_agent_is_adk_agent() -> None:
    """Foundation agent is a native ADK Agent."""
    agent = create_foundation_agent()

    assert isinstance(agent, Agent)


def test_foundation_agent_has_stable_name() -> None:
    """Foundation agent has an explicit stable name."""
    agent = create_foundation_agent()

    assert agent.name == "enterprise_foundation_agent"


def test_foundation_agent_has_instructions() -> None:
    """Foundation agent has explicit safety-oriented instructions."""
    agent = create_foundation_agent()

    instruction = agent.instruction

    assert isinstance(instruction, str)
    assert "Do not invent evidence." in instruction
