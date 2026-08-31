"""Deterministic faithfulness evaluation."""

from dataclasses import dataclass

from enterprise_ai.core.claim_support import ClaimSupport


@dataclass(frozen=True, slots=True)
class FaithfulnessResult:
    """Normalized faithfulness evaluation result."""

    score: float
    passed: bool
    faithful_claims: int
    total_claims: int

    def __post_init__(self) -> None:
        """Validate the normalized faithfulness score."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("faithfulness must be between 0 and 1")


class FaithfulnessEvaluator:
    """Measure whether claims remain faithful to supplied evidence."""

    def evaluate(
        self,
        supports: tuple[ClaimSupport, ...],
        *,
        minimum_score: float = 1.0,
    ) -> FaithfulnessResult:
        """Calculate the proportion of claims with valid support."""
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("minimum_score must be between 0 and 1")

        total_claims = len(supports)

        if total_claims == 0:
            score = 1.0
            faithful_claims = 0
        else:
            faithful_claims = sum(
                1
                for support in supports
                if support.supported
                and bool(support.evidence_ids)
                and 0.0 <= support.confidence <= 1.0
            )
            score = faithful_claims / total_claims

        return FaithfulnessResult(
            score=score,
            passed=score >= minimum_score,
            faithful_claims=faithful_claims,
            total_claims=total_claims,
        )
