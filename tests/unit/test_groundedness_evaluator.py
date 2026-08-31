"""Tests for deterministic groundedness evaluation."""

import pytest

from enterprise_ai.common.groundedness_evaluator import GroundednessEvaluator
from enterprise_ai.core.claim_support import ClaimSupport


def support(
    claim_id: str,
    *,
    evidence_ids: tuple[str, ...] = ("evidence-1",),
    supported: bool = True,
    confidence: float = 0.9,
) -> ClaimSupport:
    return ClaimSupport(
        claim_id=claim_id,
        evidence_ids=evidence_ids,
        supported=supported,
        confidence=confidence,
    )


def test_all_supported_claims_are_fully_grounded() -> None:
    result = GroundednessEvaluator().evaluate(
        (
            support("c1"),
            support("c2"),
        )
    )

    assert result.score == 1.0
    assert result.passed
    assert result.supported_claims == 2
    assert result.total_claims == 2


def test_half_supported_claims_produce_half_score() -> None:
    result = GroundednessEvaluator().evaluate(
        (
            support("c1"),
            support("c2", supported=False, evidence_ids=(), confidence=0.0),
        ),
        minimum_score=0.5,
    )

    assert result.score == pytest.approx(0.5)
    assert result.passed


def test_unsupported_claim_reduces_groundedness() -> None:
    result = GroundednessEvaluator().evaluate(
        (
            support("c1"),
            support("c2", supported=False, evidence_ids=(), confidence=0.0),
        )
    )

    assert result.score == pytest.approx(0.5)
    assert not result.passed


def test_missing_evidence_is_not_grounded() -> None:
    result = GroundednessEvaluator().evaluate(
        (
            support("c1", evidence_ids=(), supported=False, confidence=0.0),
        )
    )

    assert result.score == 0.0
    assert not result.passed


def test_empty_claim_set_is_vacuously_grounded() -> None:
    result = GroundednessEvaluator().evaluate(())

    assert result.score == 1.0
    assert result.passed


@pytest.mark.parametrize(
    "minimum_score",
    [-0.1, 1.1],
)
def test_invalid_groundedness_threshold_is_rejected(
    minimum_score: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        GroundednessEvaluator().evaluate(
            (),
            minimum_score=minimum_score,
        )

