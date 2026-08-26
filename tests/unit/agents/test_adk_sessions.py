"""ADK session integration smoke tests."""

import pytest
from google.adk.sessions import InMemorySessionService

from enterprise_ai.agents.adk.session_manager import (
    ADKSessionManager,
)


@pytest.mark.anyio
async def test_manager_uses_native_adk_session_service() -> None:
    """Session manager is backed by native ADK service."""
    manager = ADKSessionManager()

    assert isinstance(
        manager.service,
        InMemorySessionService,
    )


@pytest.mark.anyio
async def test_native_adk_session_state_round_trip() -> None:
    """Native ADK session state survives retrieval."""
    manager = ADKSessionManager()

    await manager.create(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
        state={"counter": 1},
    )

    session = await manager.get(
        app_name="enterprise-ai",
        user_id="user-001",
        session_id="session-001",
    )

    assert session is not None
    assert session.state["counter"] == 1
