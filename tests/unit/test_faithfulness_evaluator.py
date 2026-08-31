"""Tests for deterministic faithfulness evaluation."""

import pytest

from enterprise_ai.common.faithfulness_evaluator import FaithfulnessEvaluator
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


def test_fully_faithful_claim_set_scores_one() -> None:
    result = FaithfulnessEvaluator().evaluate(
        (
            support("c1"),
            support("c2"),
        )
    )

    assert result.score == 1.0
    assert result.passed
    assert result.faithful_claims == 2
    assert result.total_claims == 2


def test_partial_faithfulness_is_measured() -> None:
    result = FaithfulnessEvaluator().evaluate(
        (
            support("c1"),
            support("c2", supported=False, evidence_ids=(), confidence=0.0),
        ),
        minimum_score=0.5,
    )

    assert result.score == pytest.approx(0.5)
    assert result.passed


def test_unsupported_claim_is_not_faithful() -> None:
    result = FaithfulnessEvaluator().evaluate(
        (
            support("c1", supported=False, evidence_ids=(), confidence=0.0),
        )
    )

    assert result.score == 0.0
    assert not result.passed


def test_claim_without_evidence_is_not_faithful() -> None:
    result = FaithfulnessEvaluator().evaluate(
        (
            support("c1", evidence_ids=(), supported=False, confidence=0.0),
        )
    )

    assert result.score == 0.0
    assert not result.passed


def test_empty_claim_set_is_faithful() -> None:
    result = FaithfulnessEvaluator().evaluate(())

    assert result.score == 1.0
    assert result.passed


@pytest.mark.parametrize(
    "minimum_score",
    [-0.1, 1.1],
)
def test_invalid_faithfulness_threshold_is_rejected(
    minimum_score: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        FaithfulnessEvaluator().evaluate(
            (),
            minimum_score=minimum_score,
        )

