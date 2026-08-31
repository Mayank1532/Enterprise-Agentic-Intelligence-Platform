"""Tests for unsupported claim rate evaluation."""

import pytest

from enterprise_ai.common.unsupported_claim_rate_evaluator import (
    UnsupportedClaimRateEvaluator,
)
from enterprise_ai.core.claim_support import ClaimSupport


def make_support(claim_id: str, supported: bool) -> ClaimSupport:
    return ClaimSupport(
        claim_id=claim_id,
        evidence_ids=("e1",) if supported else (),
        supported=supported,
        confidence=1.0 if supported else 0.0,
    )


def test_all_claims_supported() -> None:
    evaluator = UnsupportedClaimRateEvaluator()

    result = evaluator.evaluate(
        (
            make_support("c1", True),
            make_support("c2", True),
        )
    )

    assert result == 0.0


def test_all_claims_unsupported() -> None:
    evaluator = UnsupportedClaimRateEvaluator()

    result = evaluator.evaluate(
        (
            make_support("c1", False),
            make_support("c2", False),
        )
    )

    assert result == 1.0


def test_partial_unsupported_claim_rate() -> None:
    evaluator = UnsupportedClaimRateEvaluator()

    result = evaluator.evaluate(
        (
            make_support("c1", True),
            make_support("c2", False),
            make_support("c3", True),
            make_support("c4", False),
        )
    )

    assert result == pytest.approx(0.5)


def test_empty_claim_set_returns_zero() -> None:
    evaluator = UnsupportedClaimRateEvaluator()

    assert evaluator.evaluate(()) == 0.0
