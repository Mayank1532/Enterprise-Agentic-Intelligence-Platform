"""Tests for ADK structured-output schema compatibility."""

from google.adk.agents import Agent

from enterprise_ai.core.structured_output import (
    AgentOutputEnvelope,
)


def test_structured_output_model_is_pydantic_model() -> None:
    """ADK-compatible output contract is a Pydantic model."""
    assert hasattr(
        AgentOutputEnvelope,
        "model_json_schema",
    )


def test_agent_accepts_output_schema_parameter() -> None:
    """Installed ADK exposes the structured output parameter."""
    agent = Agent(
        name="structured_output_test_agent",
        model="gemini-2.5-flash",
        output_schema=AgentOutputEnvelope,
    )

    assert agent.output_schema is AgentOutputEnvelope
