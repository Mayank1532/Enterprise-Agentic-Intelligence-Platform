"""Tests for deterministic agent context."""

from enterprise_ai.agents.adk.context import AgentContext


def test_context_is_created_from_session_state() -> None:
    """Context captures session identity and state."""
    context = AgentContext.from_session(
        session_id="session-001",
        user_id="user-001",
        state={
            "topic": "retrieval",
            "language": "en",
        },
    )

    assert context.session_id == "session-001"
    assert context.user_id == "user-001"
    assert context.get("topic") == "retrieval"
    assert context.get("language") == "en"


def test_context_missing_value_returns_default() -> None:
    """Missing context values return the supplied default."""
    context = AgentContext.from_session(
        session_id="session-001",
        user_id="user-001",
        state={},
    )

    assert context.get("missing", "default") == "default"


def test_context_is_snapshot_not_mutable_state() -> None:
    """Context remains unchanged after source state mutation."""
    state = {
        "topic": "retrieval",
    }

    context = AgentContext.from_session(
        session_id="session-001",
        user_id="user-001",
        state=state,
    )

    state["topic"] = "different"

    assert context.get("topic") == "retrieval"


def test_context_values_are_deterministically_ordered() -> None:
    """Context state ordering is deterministic."""
    context = AgentContext.from_session(
        session_id="session-001",
        user_id="user-001",
        state={
            "z": 3,
            "a": 1,
            "m": 2,
        },
    )

    assert context.values == (
        ("a", 1),
        ("m", 2),
        ("z", 3),
    )
