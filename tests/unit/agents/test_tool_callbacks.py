"""Tests for deterministic tool lifecycle policies."""

from unittest.mock import Mock

from enterprise_ai.agents.adk.tool_callbacks import (
    ToolLifecyclePolicy,
)
from enterprise_ai.core.callback import CallbackAction


def make_tool_context(session_id: str) -> Mock:
    """Create a minimal tool context double."""
    context = Mock()
    context.session.id = session_id
    return context


def test_before_tool_allows_valid_session() -> None:
    """Tool execution continues with a valid session."""
    context = make_tool_context("session-001")

    decision = ToolLifecyclePolicy().before_tool(context)

    assert decision.action is CallbackAction.CONTINUE
    assert decision.allowed is True


def test_before_tool_abstains_without_session_identity() -> None:
    """Tool execution abstains without session identity."""
    context = make_tool_context("")

    decision = ToolLifecyclePolicy().before_tool(context)

    assert decision.action is CallbackAction.ABSTAIN
    assert decision.allowed is False
    assert "session" in decision.reason


def test_after_tool_is_deterministic() -> None:
    """Tool completion produces a deterministic decision."""
    context = make_tool_context("session-001")

    decision = ToolLifecyclePolicy().after_tool(context)

    assert decision.action is CallbackAction.CONTINUE
    assert decision.reason == "tool lifecycle completed"
