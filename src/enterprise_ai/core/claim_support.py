"""Domain contract describing claim-to-evidence support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimSupport:
    """Result of matching a claim against available evidence."""

    claim_id: str
    evidence_ids: tuple[str, ...]
    supported: bool
    confidence: float

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id must not be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")

        if self.supported and not self.evidence_ids:
            raise ValueError("supported claims must reference at least one evidence item.")
