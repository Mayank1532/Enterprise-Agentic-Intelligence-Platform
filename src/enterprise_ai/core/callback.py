"""Deterministic callback decisions."""

from dataclasses import dataclass
from enum import StrEnum


class CallbackAction(StrEnum):
    """Allowed lifecycle callback actions."""

    CONTINUE = "continue"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class CallbackDecision:
    """Deterministic decision produced by a lifecycle policy."""

    action: CallbackAction
    reason: str

    @property
    def allowed(self) -> bool:
        """Return whether execution may continue."""
        return self.action is CallbackAction.CONTINUE
