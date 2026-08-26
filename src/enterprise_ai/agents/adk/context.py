"""Deterministic ADK context boundary."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentContext:
    """Application-level context passed into an agent invocation."""

    session_id: str
    user_id: str
    values: tuple[tuple[str, Any], ...]

    @classmethod
    def from_session(
        cls,
        session_id: str,
        user_id: str,
        state: dict[str, Any],
    ) -> "AgentContext":
        """Create an immutable context snapshot."""
        return cls(
            session_id=session_id,
            user_id=user_id,
            values=tuple(sorted(state.items())),
        )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read a value from the immutable context snapshot."""
        for item_key, item_value in self.values:
            if item_key == key:
                return item_value

        return default
