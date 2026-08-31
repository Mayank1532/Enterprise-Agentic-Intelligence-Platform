"""Unsupported claim rate evaluation."""

from dataclasses import dataclass

from enterprise_ai.core.claim_support import ClaimSupport


@dataclass(frozen=True, slots=True)
class UnsupportedClaimRateEvaluator:
    """Evaluate the proportion of claims that lack supporting evidence."""

    def evaluate(
        self,
        claim_supports: tuple[ClaimSupport, ...],
    ) -> float:
        """Return the fraction of unsupported claims."""
        if not claim_supports:
            return 0.0

        unsupported = sum(
            1
            for support in claim_supports
            if not support.supported
        )

        return unsupported / len(claim_supports)
