"""Tests for callback decisions."""

from enterprise_ai.core.callback import (
    CallbackAction,
    CallbackDecision,
)


def test_continue_decision_is_allowed() -> None:
    """Continue decisions permit execution."""
    decision = CallbackDecision(
        action=CallbackAction.CONTINUE,
        reason="valid",
    )

    assert decision.allowed is True


def test_abstain_decision_is_not_allowed() -> None:
    """Abstain decisions block execution."""
    decision = CallbackDecision(
        action=CallbackAction.ABSTAIN,
        reason="insufficient context",
    )

    assert decision.allowed is False


def test_callback_decision_is_immutable() -> None:
    """Callback decisions are immutable."""
    decision = CallbackDecision(
        action=CallbackAction.CONTINUE,
        reason="valid",
    )

    try:
        decision.reason = "changed"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("CallbackDecision must be immutable.")
