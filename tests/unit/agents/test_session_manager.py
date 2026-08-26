"""Tests for ADK session management."""

import pytest

from enterprise_ai.agents.adk.session_manager import (
    ADKSessionManager,
)


@pytest.mark.anyio
async def test_create_session_with_initial_state() -> None:
    """Session preserves explicit initial state."""
    manager = ADKSessionManager()

    session = await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
        state={
            "tenant": "tenant-a",
            "mode": "research",
        },
    )

    assert session.id == "session-001"
    assert session.user_id == "user-001"
    assert session.app_name == "enterprise-ai"
    assert session.state["tenant"] == "tenant-a"
    assert session.state["mode"] == "research"


@pytest.mark.anyio
async def test_get_existing_session() -> None:
    """Existing session can be retrieved."""
    manager = ADKSessionManager()

    await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    session = await manager.get(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    assert session is not None
    assert session.id == "session-001"


@pytest.mark.anyio
async def test_missing_session_returns_none() -> None:
    """Unknown session returns None."""
    manager = ADKSessionManager()

    session = await manager.get(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="missing",
    )

    assert session is None


@pytest.mark.anyio
async def test_state_mutation_is_session_local() -> None:
    """State mutation belongs to the selected session."""
    manager = ADKSessionManager()

    first = await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    second = await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-002",
    )

    manager.set_state(
        first,
        "topic",
        "retrieval",
    )

    assert manager.get_state(first, "topic") == "retrieval"
    assert manager.get_state(second, "topic") is None


@pytest.mark.anyio
async def test_sessions_are_isolated() -> None:
    """Two sessions cannot observe each other's state."""
    manager = ADKSessionManager()

    first = await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
        state={"secret": "first"},
    )

    second = await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-002",
        state={"secret": "second"},
    )

    assert first.state["secret"] == "first"
    assert second.state["secret"] == "second"


@pytest.mark.anyio
async def test_delete_session() -> None:
    """Deleted session is no longer retrievable."""
    manager = ADKSessionManager()

    await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    await manager.delete(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    session = await manager.get(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    assert session is None
