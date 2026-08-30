"""Minimal deterministic grounding evaluation dataset."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GroundingEvaluationCase:
    """A single deterministic grounding evaluation case."""

    name: str
    expected_grounded: bool
    expected_abstain: bool
    claim_ids: tuple[str, ...]
    support_claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    supported_claim_ids: tuple[str, ...]
    confidences: tuple[float, ...]
    minimum_confidence: float
    minimum_supported_claims: float


GROUNDING_EVALUATION_CASES = (
    GroundingEvaluationCase(
        name="fully_supported",
        expected_grounded=True,
        expected_abstain=False,
        claim_ids=("claim-1",),
        support_claim_ids=("claim-1",),
        evidence_ids=("evidence-1",),
        supported_claim_ids=("claim-1",),
        confidences=(0.90,),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="unsupported_claim",
        expected_grounded=False,
        expected_abstain=True,
        claim_ids=("claim-1",),
        support_claim_ids=("claim-1",),
        evidence_ids=(),
        supported_claim_ids=(),
        confidences=(0.10,),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="low_confidence",
        expected_grounded=False,
        expected_abstain=True,
        claim_ids=("claim-1",),
        support_claim_ids=("claim-1",),
        evidence_ids=("evidence-1",),
        supported_claim_ids=("claim-1",),
        confidences=(0.60,),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="missing_evidence",
        expected_grounded=False,
        expected_abstain=True,
        claim_ids=("claim-1",),
        support_claim_ids=("claim-1",),
        evidence_ids=(),
        supported_claim_ids=("claim-1",),
        confidences=(0.95,),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="invalid_evidence_reference",
        expected_grounded=False,
        expected_abstain=True,
        claim_ids=("claim-1",),
        support_claim_ids=("claim-1",),
        evidence_ids=("different-evidence",),
        supported_claim_ids=("claim-1",),
        confidences=(0.95,),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="multiple_claims_fully_supported",
        expected_grounded=True,
        expected_abstain=False,
        claim_ids=("claim-1", "claim-2"),
        support_claim_ids=("claim-1", "claim-2"),
        evidence_ids=("evidence-1", "evidence-2"),
        supported_claim_ids=("claim-1", "claim-2"),
        confidences=(0.90, 0.85),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="partial_support_strict_policy",
        expected_grounded=False,
        expected_abstain=True,
        claim_ids=("claim-1", "claim-2"),
        support_claim_ids=("claim-1", "claim-2"),
        evidence_ids=("evidence-1",),
        supported_claim_ids=("claim-1",),
        confidences=(0.90, 0.10),
        minimum_confidence=0.70,
        minimum_supported_claims=1.0,
    ),
    GroundingEvaluationCase(
        name="partial_support_configured_policy",
        expected_grounded=True,
        expected_abstain=False,
        claim_ids=("claim-1", "claim-2"),
        support_claim_ids=("claim-1", "claim-2"),
        evidence_ids=("evidence-1",),
        supported_claim_ids=("claim-1",),
        confidences=(0.90, 0.10),
        minimum_confidence=0.70,
        minimum_supported_claims=0.50,
    ),
)
