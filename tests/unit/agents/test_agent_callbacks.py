"""Tests for deterministic ADK agent lifecycle policy."""

from unittest.mock import Mock

from google.adk.agents.callback_context import CallbackContext

from enterprise_ai.agents.adk.agent_callbacks import (
    AgentLifecyclePolicy,
)
from enterprise_ai.core.callback import CallbackAction


def make_context(session: object | None) -> Mock:
    """Create a callback context double using the public session property."""
    context = Mock(spec=CallbackContext)
    context.session = session
    return context


def test_before_agent_allows_valid_session() -> None:
    """Agent execution continues when a session exists."""
    context = make_context(Mock())

    decision = AgentLifecyclePolicy().before_agent(context)

    assert context.session is not None
    assert decision.action is CallbackAction.CONTINUE
    assert decision.allowed is True
    assert decision.reason == "agent session is available"


def test_before_agent_abstains_without_session() -> None:
    """Agent execution abstains when session state is unavailable."""
    context = make_context(None)

    decision = AgentLifecyclePolicy().before_agent(context)

    assert context.session is None
    assert decision.action is CallbackAction.ABSTAIN
    assert decision.allowed is False
    assert "session" in decision.reason


def test_after_agent_is_deterministic() -> None:
    """Agent completion produces a deterministic decision."""
    context = make_context(Mock())

    decision = AgentLifecyclePolicy().after_agent(context)

    assert decision.action is CallbackAction.CONTINUE
    assert decision.reason == "agent lifecycle completed"
