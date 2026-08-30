"""Tests defining deterministic grounding verification behavior."""

import pytest

from enterprise_ai.core.claim import Claim
from enterprise_ai.core.claim_support import ClaimSupport
from enterprise_ai.core.grounding_policy import GroundingPolicy
from enterprise_ai.core.grounding_result import GroundingResult

# NOTE:
# The verifier implementation does not exist yet.
#
# These tests intentionally describe the required behavior.
# Phase 7E is test-first: implementation comes after the
# contract has been established.


def make_claim(
    claim_id: str = "claim-1",
    text: str = "The system supports evidence-grounded answers.",
) -> Claim:
    """Create a valid test claim."""
    return Claim(
        claim_id=claim_id,
        text=text,
    )


def make_support(
    claim_id: str = "claim-1",
    evidence_ids: tuple[str, ...] = ("evidence-1",),
    supported: bool = True,
    confidence: float = 0.90,
) -> ClaimSupport:
    """Create a valid claim-support result."""
    return ClaimSupport(
        claim_id=claim_id,
        evidence_ids=evidence_ids,
        supported=supported,
        confidence=confidence,
    )


# ============================================================
# Required verifier contract
# ============================================================


def test_grounding_verifier_exists() -> None:
    """The Phase 7 verifier must expose a stable verification API."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    assert verifier is not None


def test_supported_claim_with_valid_evidence_is_grounded() -> None:
    """A sufficiently confident supported claim should be grounded."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(make_support(),),
        evidence_ids={"evidence-1"},
    )

    assert isinstance(result, GroundingResult)
    assert result.grounded is True
    assert result.abstain is False
    assert result.confidence >= 0.70


def test_unsupported_claim_causes_abstention() -> None:
    """An explicitly unsupported claim must not be accepted."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(
            make_support(
                supported=False,
                evidence_ids=(),
                confidence=0.10,
            ),
        ),
        evidence_ids=set(),
    )

    assert result.grounded is False
    assert result.abstain is True
    assert result.supports[0].supported is False


def test_insufficient_confidence_causes_abstention() -> None:
    """Evidence below the configured confidence threshold is insufficient."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(
            make_support(
                confidence=0.60,
            ),
        ),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is False
    assert result.abstain is True
    assert result.confidence == pytest.approx(0.60)


def test_confidence_at_threshold_is_accepted() -> None:
    """Confidence exactly at the configured threshold is acceptable."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(
            make_support(
                confidence=0.70,
            ),
        ),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is True
    assert result.abstain is False


def test_invalid_evidence_reference_causes_abstention() -> None:
    """A support result referencing unavailable evidence is invalid."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(
            make_support(
                evidence_ids=("missing-evidence",),
                confidence=0.95,
            ),
        ),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is False
    assert result.abstain is True
    assert any("evidence" in reason.lower() for reason in result.reasons)


def test_empty_evidence_causes_abstention() -> None:
    """No evidence means the answer cannot be grounded."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(
            make_support(
                evidence_ids=(),
                supported=False,
                confidence=0.0,
            ),
        ),
        evidence_ids=set(),
    )

    assert result.grounded is False
    assert result.abstain is True


def test_multiple_claims_require_configured_support_ratio() -> None:
    """Support ratio must respect the configured policy."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    claims = (
        make_claim(
            claim_id="claim-1",
            text="First factual claim.",
        ),
        make_claim(
            claim_id="claim-2",
            text="Second factual claim.",
        ),
    )

    supports = (
        make_support(
            claim_id="claim-1",
            evidence_ids=("evidence-1",),
            supported=True,
            confidence=0.90,
        ),
        make_support(
            claim_id="claim-2",
            evidence_ids=(),
            supported=False,
            confidence=0.10,
        ),
    )

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    result = verifier.verify(
        claims=claims,
        supports=supports,
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is False
    assert result.abstain is True


def test_multiple_claims_can_pass_with_partial_support_policy() -> None:
    """A configurable support ratio can allow partial support."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    claims = (
        make_claim(
            claim_id="claim-1",
            text="First factual claim.",
        ),
        make_claim(
            claim_id="claim-2",
            text="Second factual claim.",
        ),
    )

    supports = (
        make_support(
            claim_id="claim-1",
            evidence_ids=("evidence-1",),
            supported=True,
            confidence=0.90,
        ),
        make_support(
            claim_id="claim-2",
            evidence_ids=(),
            supported=False,
            confidence=0.10,
        ),
    )

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=0.50,
        )
    )

    result = verifier.verify(
        claims=claims,
        supports=supports,
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is True
    assert result.abstain is False


def test_claim_without_matching_support_is_unsupported() -> None:
    """Every claim must have a corresponding support record."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(
            make_claim(
                claim_id="claim-1",
            ),
        ),
        supports=(),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is False
    assert result.abstain is True


def test_unknown_support_claim_id_is_rejected() -> None:
    """Support for a non-existent claim must not be accepted."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(
            make_claim(
                claim_id="claim-1",
            ),
        ),
        supports=(
            make_support(
                claim_id="claim-unknown",
                evidence_ids=("evidence-1",),
                confidence=0.95,
            ),
        ),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is False
    assert result.abstain is True


def test_reasons_are_present_for_abstention() -> None:
    """An abstention result must explain why grounding failed."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(),
        evidence_ids=set(),
    )

    assert result.abstain is True
    assert result.reasons
    assert all(reason.strip() for reason in result.reasons)


def test_grounded_result_contains_support_records() -> None:
    """A grounded result must preserve its claim support records."""
    from enterprise_ai.common.grounding_verifier import GroundingVerifier

    support = make_support()

    verifier = GroundingVerifier()

    result = verifier.verify(
        claims=(make_claim(),),
        supports=(support,),
        evidence_ids={"evidence-1"},
    )

    assert result.grounded is True
    assert result.supports == (support,)
