"""Tests for the minimal Phase 7 grounding evaluation dataset."""

from grounding_evaluation import (
    GROUNDING_EVALUATION_CASES,
    GroundingEvaluationCase,
)

from enterprise_ai.common.grounding_verifier import GroundingVerifier
from enterprise_ai.core.claim import Claim
from enterprise_ai.core.claim_support import ClaimSupport
from enterprise_ai.core.grounding_policy import GroundingPolicy
from enterprise_ai.core.grounding_result import GroundingResult


def build_claims(case: GroundingEvaluationCase) -> tuple[Claim, ...]:
    """Build claims from an evaluation case."""
    return tuple(
        Claim(
            claim_id=claim_id,
            text=f"Evaluation claim {claim_id}.",
        )
        for claim_id in case.claim_ids
    )


def build_supports(
    case: GroundingEvaluationCase,
) -> tuple[ClaimSupport, ...]:
    """Build claim support records from an evaluation case."""
    supports: list[ClaimSupport] = []

    for index, claim_id in enumerate(case.support_claim_ids):
        supported = claim_id in case.supported_claim_ids

        # A supported ClaimSupport must reference evidence.
        # The missing_evidence case therefore represents the
        # claim as unsupported rather than constructing an
        # invalid ClaimSupport object.
        if case.name == "missing_evidence":
            supported = False

        confidence = case.confidences[min(index, len(case.confidences) - 1)]

        evidence_ids = ("evidence-1",) if supported and "evidence-1" in case.evidence_ids else ()

        if supported and claim_id == "claim-2" and "evidence-2" in case.evidence_ids:
            evidence_ids = ("evidence-2",)

        if case.name == "invalid_evidence_reference":
            evidence_ids = ("missing-evidence",)

        supports.append(
            ClaimSupport(
                claim_id=claim_id,
                evidence_ids=evidence_ids,
                supported=supported,
                confidence=confidence,
            )
        )

    return tuple(supports)


def evaluate_case(
    case: GroundingEvaluationCase,
) -> GroundingResult:
    """Run one evaluation case through the verifier."""
    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=case.minimum_confidence,
            minimum_supported_claims=case.minimum_supported_claims,
        )
    )

    return verifier.verify(
        claims=build_claims(case),
        supports=build_supports(case),
        evidence_ids=set(case.evidence_ids),
    )


# ============================================================
# Dataset integrity
# ============================================================


def test_evaluation_dataset_has_expected_size() -> None:
    """Keep the evaluation dataset intentionally small."""
    assert len(GROUNDING_EVALUATION_CASES) == 8


def test_evaluation_case_names_are_unique() -> None:
    """Every evaluation scenario must have a unique name."""
    names = [case.name for case in GROUNDING_EVALUATION_CASES]

    assert len(names) == len(set(names))


# ============================================================
# Evaluation behavior
# ============================================================


def test_every_evaluation_case_matches_expected_result() -> None:
    """Every dataset case must produce its declared result."""
    for case in GROUNDING_EVALUATION_CASES:
        result = evaluate_case(case)

        assert result.grounded is case.expected_grounded, case.name
        assert result.abstain is case.expected_abstain, case.name


def test_fully_supported_case_is_grounded() -> None:
    """Supported evidence should be accepted."""
    case = next(case for case in GROUNDING_EVALUATION_CASES if case.name == "fully_supported")

    result = evaluate_case(case)

    assert result.grounded is True
    assert result.abstain is False
    assert result.confidence == 0.90


def test_unsupported_case_abstains() -> None:
    """Unsupported claims must be rejected."""
    case = next(case for case in GROUNDING_EVALUATION_CASES if case.name == "unsupported_claim")

    result = evaluate_case(case)

    assert result.grounded is False
    assert result.abstain is True


def test_low_confidence_case_abstains() -> None:
    """Low-confidence support must be rejected."""
    case = next(case for case in GROUNDING_EVALUATION_CASES if case.name == "low_confidence")

    result = evaluate_case(case)

    assert result.grounded is False
    assert result.abstain is True


def test_missing_evidence_case_abstains() -> None:
    """Claims without available evidence must be rejected."""
    case = next(case for case in GROUNDING_EVALUATION_CASES if case.name == "missing_evidence")

    result = evaluate_case(case)

    assert result.grounded is False
    assert result.abstain is True


def test_invalid_reference_case_abstains() -> None:
    """Invalid evidence references must be rejected."""
    case = next(
        case for case in GROUNDING_EVALUATION_CASES if case.name == "invalid_evidence_reference"
    )

    result = evaluate_case(case)

    assert result.grounded is False
    assert result.abstain is True


def test_full_multi_claim_case_is_grounded() -> None:
    """All fully supported claims should pass."""
    case = next(
        case
        for case in GROUNDING_EVALUATION_CASES
        if case.name == "multiple_claims_fully_supported"
    )

    result = evaluate_case(case)

    assert result.grounded is True
    assert result.abstain is False


def test_strict_partial_support_abstains() -> None:
    """Strict policy requires every claim to be supported."""
    case = next(
        case for case in GROUNDING_EVALUATION_CASES if case.name == "partial_support_strict_policy"
    )

    result = evaluate_case(case)

    assert result.grounded is False
    assert result.abstain is True


def test_configured_partial_support_is_allowed() -> None:
    """Support ratio policy can intentionally allow partial support."""
    case = next(
        case
        for case in GROUNDING_EVALUATION_CASES
        if case.name == "partial_support_configured_policy"
    )

    result = evaluate_case(case)

    assert result.grounded is True
    assert result.abstain is False


def test_evaluation_cases_provide_reasons_on_failure() -> None:
    """Rejected cases must explain the grounding failure."""
    for case in GROUNDING_EVALUATION_CASES:
        result = evaluate_case(case)

        if case.expected_abstain:
            assert result.reasons
            assert all(reason.strip() for reason in result.reasons)
