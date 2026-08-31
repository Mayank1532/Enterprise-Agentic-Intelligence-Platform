"""Tests for deterministic retrieval precision evaluation."""

import pytest

from enterprise_ai.common.retrieval_precision_evaluator import (
    RetrievalPrecisionEvaluator,
)
from enterprise_ai.core.evaluation_case import EvaluationCase
from enterprise_ai.core.evaluation_dimension import EvaluationDimension


def make_case(*evidence_ids: str) -> EvaluationCase:
    return EvaluationCase(
        case_id="retrieval-precision-1",
        query="test query",
        expected_evidence_ids=evidence_ids,
    )


def test_precision_is_one_when_all_retrieved_evidence_is_relevant() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case("e1", "e2"),
        ("e1", "e2"),
    )

    assert outcome.dimension == EvaluationDimension.RETRIEVAL_PRECISION
    assert outcome.value == 1.0
    assert outcome.passed is True


def test_precision_is_half_when_half_of_results_are_relevant() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case("e1", "e2"),
        ("e1", "irrelevant"),
    )

    assert outcome.value == 0.5
    assert outcome.passed is False


def test_precision_is_zero_when_no_retrieved_result_is_relevant() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case("e1", "e2"),
        ("irrelevant-1", "irrelevant-2"),
    )

    assert outcome.value == 0.0
    assert outcome.passed is False


def test_precision_is_one_for_empty_retrieval_when_no_evidence_is_expected() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case(),
        (),
    )

    assert outcome.value == 1.0
    assert outcome.passed is True


def test_precision_is_zero_for_empty_retrieval_when_evidence_is_expected() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case("e1"),
        (),
    )

    assert outcome.value == 0.0
    assert outcome.passed is False


def test_duplicate_retrievals_are_counted_as_retrieved_items() -> None:
    outcome = RetrievalPrecisionEvaluator.evaluate(
        make_case("e1"),
        ("e1", "e1", "irrelevant"),
    )

    assert outcome.value == pytest.approx(2 / 3)
    assert outcome.passed is False
