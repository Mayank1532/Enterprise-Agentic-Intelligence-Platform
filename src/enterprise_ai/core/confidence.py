"""Deterministic retrieval confidence representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    """Normalized confidence information for a retrieval result."""

    value: float
    basis: str

    def __post_init__(self) -> None:
        """Validate confidence bounds."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        if not self.basis.strip():
            raise ValueError("confidence basis must not be empty")
