"""Tests for Phase 7 grounding domain contracts."""

import pytest

from enterprise_ai.core.claim import Claim
from enterprise_ai.core.claim_support import ClaimSupport
from enterprise_ai.core.grounding_policy import GroundingPolicy
from enterprise_ai.core.grounding_result import GroundingResult

# ============================================================
# Claim
# ============================================================


def test_claim_accepts_valid_values() -> None:
    claim = Claim(
        claim_id="claim-1",
        text="The system provides evidence-grounded answers.",
    )

    assert claim.claim_id == "claim-1"
    assert claim.text == "The system provides evidence-grounded answers."


@pytest.mark.parametrize(
    ("claim_id", "text"),
    [
        ("", "A valid claim."),
        ("   ", "A valid claim."),
        ("claim-1", ""),
        ("claim-1", "   "),
    ],
)
def test_claim_rejects_empty_values(
    claim_id: str,
    text: str,
) -> None:
    with pytest.raises(ValueError):
        Claim(
            claim_id=claim_id,
            text=text,
        )


# ============================================================
# ClaimSupport
# ============================================================


def test_claim_support_accepts_supported_claim() -> None:
    support = ClaimSupport(
        claim_id="claim-1",
        evidence_ids=("evidence-1",),
        supported=True,
        confidence=0.90,
    )

    assert support.claim_id == "claim-1"
    assert support.evidence_ids == ("evidence-1",)
    assert support.supported is True
    assert support.confidence == 0.90


def test_claim_support_accepts_unsupported_claim_without_evidence() -> None:
    support = ClaimSupport(
        claim_id="claim-1",
        evidence_ids=(),
        supported=False,
        confidence=0.20,
    )

    assert support.supported is False
    assert support.evidence_ids == ()


@pytest.mark.parametrize(
    "confidence",
    [-0.01, 1.01],
)
def test_claim_support_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValueError):
        ClaimSupport(
            claim_id="claim-1",
            evidence_ids=("evidence-1",),
            supported=True,
            confidence=confidence,
        )


def test_claim_support_rejects_empty_claim_id() -> None:
    with pytest.raises(ValueError):
        ClaimSupport(
            claim_id="",
            evidence_ids=("evidence-1",),
            supported=True,
            confidence=0.90,
        )


def test_claim_support_rejects_supported_claim_without_evidence() -> None:
    with pytest.raises(ValueError):
        ClaimSupport(
            claim_id="claim-1",
            evidence_ids=(),
            supported=True,
            confidence=0.90,
        )


# ============================================================
# GroundingPolicy
# ============================================================


def test_grounding_policy_has_safe_defaults() -> None:
    policy = GroundingPolicy()

    assert policy.minimum_confidence == 0.70
    assert policy.minimum_supported_claims == 1.0


@pytest.mark.parametrize(
    "confidence",
    [-0.01, 1.01],
)
def test_grounding_policy_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValueError):
        GroundingPolicy(
            minimum_confidence=confidence,
        )


@pytest.mark.parametrize(
    "supported_claims",
    [-0.01, 1.01],
)
def test_grounding_policy_rejects_invalid_support_threshold(
    supported_claims: float,
) -> None:
    with pytest.raises(ValueError):
        GroundingPolicy(
            minimum_supported_claims=supported_claims,
        )


def test_grounding_policy_accepts_custom_thresholds() -> None:
    policy = GroundingPolicy(
        minimum_confidence=0.80,
        minimum_supported_claims=0.75,
    )

    assert policy.minimum_confidence == 0.80
    assert policy.minimum_supported_claims == 0.75


# ============================================================
# GroundingResult
# ============================================================


def test_grounding_result_accepts_grounded_result() -> None:
    support = ClaimSupport(
        claim_id="claim-1",
        evidence_ids=("evidence-1",),
        supported=True,
        confidence=0.90,
    )

    result = GroundingResult(
        grounded=True,
        confidence=0.90,
        supports=(support,),
        reasons=("Claim is supported by evidence.",),
        abstain=False,
    )

    assert result.grounded is True
    assert result.confidence == 0.90
    assert result.abstain is False
    assert result.supports == (support,)


def test_grounding_result_accepts_abstention() -> None:
    result = GroundingResult(
        grounded=False,
        confidence=0.20,
        supports=(),
        reasons=("Insufficient evidence.",),
        abstain=True,
    )

    assert result.grounded is False
    assert result.abstain is True
    assert result.supports == ()


@pytest.mark.parametrize(
    "confidence",
    [-0.01, 1.01],
)
def test_grounding_result_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValueError):
        GroundingResult(
            grounded=False,
            confidence=confidence,
            supports=(),
            reasons=("Insufficient evidence.",),
            abstain=True,
        )


def test_grounding_result_rejects_grounded_abstention_conflict() -> None:
    with pytest.raises(ValueError):
        GroundingResult(
            grounded=True,
            confidence=0.90,
            supports=(),
            reasons=("Grounded answer.",),
            abstain=True,
        )
