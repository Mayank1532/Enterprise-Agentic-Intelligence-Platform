"""Deterministic groundedness evaluation."""

from dataclasses import dataclass

from enterprise_ai.core.claim_support import ClaimSupport


@dataclass(frozen=True, slots=True)
class GroundednessResult:
    """Normalized groundedness evaluation result."""

    score: float
    passed: bool
    supported_claims: int
    total_claims: int

    def __post_init__(self) -> None:
        """Validate the normalized groundedness score."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("groundedness must be between 0 and 1")

        if self.supported_claims < 0:
            raise ValueError("supported_claims must not be negative")

        if self.total_claims < 0:
            raise ValueError("total_claims must not be negative")

        if self.supported_claims > self.total_claims:
            raise ValueError(
                "supported_claims cannot exceed total_claims"
            )


class GroundednessEvaluator:
    """Measure the proportion of claims supported by valid evidence."""

    def evaluate(
        self,
        supports: tuple[ClaimSupport, ...],
        *,
        minimum_score: float = 1.0,
    ) -> GroundednessResult:
        """Calculate the supported-claim ratio."""
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("minimum_score must be between 0 and 1")

        total_claims = len(supports)

        if total_claims == 0:
            score = 1.0
            supported_claims = 0
        else:
            supported_claims = sum(
                1
                for support in supports
                if support.supported
                and bool(support.evidence_ids)
                and support.confidence > 0.0
            )
            score = supported_claims / total_claims

        return GroundednessResult(
            score=score,
            passed=score >= minimum_score,
            supported_claims=supported_claims,
            total_claims=total_claims,
        )
