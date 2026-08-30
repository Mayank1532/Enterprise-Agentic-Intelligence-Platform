"""Deterministic verification of claims against supplied evidence."""

from enterprise_ai.core.claim import Claim
from enterprise_ai.core.claim_support import ClaimSupport
from enterprise_ai.core.grounding_policy import GroundingPolicy
from enterprise_ai.core.grounding_result import GroundingResult


class GroundingVerifier:
    """Verify whether claims are sufficiently supported by evidence."""

    def __init__(
        self,
        policy: GroundingPolicy | None = None,
    ) -> None:
        """Initialize the verifier with a grounding policy."""
        self.policy = policy or GroundingPolicy()

    def verify(
        self,
        claims: tuple[Claim, ...],
        supports: tuple[ClaimSupport, ...],
        evidence_ids: set[str],
    ) -> GroundingResult:
        """Verify claims against the supplied evidence identifiers."""

        if not claims:
            return GroundingResult(
                grounded=False,
                confidence=0.0,
                supports=supports,
                reasons=("No claims were supplied.",),
                abstain=True,
            )

        support_by_claim = {support.claim_id: support for support in supports}

        reasons: list[str] = []
        valid_support_count = 0
        confidence_values: list[float] = []

        for claim in claims:
            support = support_by_claim.get(claim.claim_id)

            if support is None:
                reasons.append(f"Claim '{claim.claim_id}' has no matching support record.")
                continue

            if support.claim_id != claim.claim_id:
                reasons.append(f"Support claim ID does not match claim '{claim.claim_id}'.")
                continue

            missing_evidence = set(support.evidence_ids) - evidence_ids

            if missing_evidence:
                reasons.append(
                    f"Claim '{claim.claim_id}' references unavailable "
                    f"evidence: {', '.join(sorted(missing_evidence))}."
                )
                continue

            if not support.supported:
                reasons.append(f"Claim '{claim.claim_id}' is explicitly unsupported.")
                continue

            if not support.evidence_ids:
                reasons.append(f"Claim '{claim.claim_id}' has no evidence.")
                continue

            if support.confidence < self.policy.minimum_confidence:
                reasons.append(
                    f"Claim '{claim.claim_id}' confidence "
                    f"{support.confidence:.2f} is below the required "
                    f"threshold {self.policy.minimum_confidence:.2f}."
                )
                confidence_values.append(support.confidence)
                continue

            valid_support_count += 1
            confidence_values.append(support.confidence)

        support_ratio = valid_support_count / len(claims)

        if confidence_values:
            overall_confidence = sum(confidence_values) / len(confidence_values)
        else:
            overall_confidence = 0.0

        grounded = (
            support_ratio >= self.policy.minimum_supported_claims
            and overall_confidence >= self.policy.minimum_confidence
            and valid_support_count > 0
        )

        if grounded:
            reasons.append("All required grounding conditions were satisfied.")
            return GroundingResult(
                grounded=True,
                confidence=overall_confidence,
                supports=supports,
                reasons=tuple(reasons),
                abstain=False,
            )

        if not reasons:
            reasons.append("Grounding requirements were not satisfied.")

        return GroundingResult(
            grounded=False,
            confidence=overall_confidence,
            supports=supports,
            reasons=tuple(reasons),
            abstain=True,
        )
