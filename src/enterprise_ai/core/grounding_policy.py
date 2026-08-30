"""Policy contract controlling grounding decisions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GroundingPolicy:
    """Thresholds used to decide whether an answer is grounded."""

    minimum_confidence: float = 0.70
    minimum_supported_claims: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0.0 and 1.0.")

        if not 0.0 <= self.minimum_supported_claims <= 1.0:
            raise ValueError("minimum_supported_claims must be between 0.0 and 1.0.")
