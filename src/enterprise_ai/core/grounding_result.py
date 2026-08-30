"""Domain contract representing the result of grounding verification."""

from dataclasses import dataclass

from enterprise_ai.core.claim_support import ClaimSupport


@dataclass(frozen=True)
class GroundingResult:
    """Aggregated result of grounding validation."""

    grounded: bool
    confidence: float
    supports: tuple[ClaimSupport, ...]
    reasons: tuple[str, ...]
    abstain: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")

        if self.grounded and self.abstain:
            raise ValueError("A grounded result cannot simultaneously require abstention.")
