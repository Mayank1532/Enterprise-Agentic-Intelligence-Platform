"""Deterministic Google ADK session management."""

from typing import Any

from google.adk.sessions import InMemorySessionService
from google.adk.sessions.session import Session


class ADKSessionManager:
    """Manage isolated in-memory ADK sessions."""

    def __init__(
        self,
        service: InMemorySessionService | None = None,
    ) -> None:
        """Initialize the session manager."""
        self._service = service or InMemorySessionService()

    @property
    def service(self) -> InMemorySessionService:
        """Return the underlying ADK session service."""
        return self._service

    async def create(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: dict[str, Any] | None = None,
    ) -> Session:
        """Create a new isolated session."""
        return await self._service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=state or {},
        )

    async def get(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Session | None:
        """Retrieve an existing session."""
        return await self._service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    async def delete(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """Delete an existing session."""
        await self._service.delete_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    @staticmethod
    def set_state(
        session: Session,
        key: str,
        value: Any,
    ) -> None:
        """Set one state value on a session."""
        session.state[key] = value

    @staticmethod
    def get_state(
        session: Session,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read one state value from a session."""
        return session.state.get(key, default)
