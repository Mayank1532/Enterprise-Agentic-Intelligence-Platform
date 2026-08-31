"""Tests for deterministic reranker effectiveness evaluation."""

import pytest

from enterprise_ai.common.reranker_effectiveness_evaluator import (
    RerankerEffectivenessEvaluator,
)


def test_perfect_ranking_scores_one() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("a", "b", "c"),
        ("a", "b", "c"),
    )

    assert result.score == 1.0
    assert result.passed


def test_reversed_ranking_is_not_perfect() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("c", "b", "a"),
        ("a", "b", "c"),
    )

    assert result.score < 1.0
    assert not result.passed


def test_empty_expected_and_empty_actual_pass() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        (),
        (),
    )

    assert result.score == 1.0
    assert result.passed


def test_empty_expected_with_actual_items_fails() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("a",),
        (),
    )

    assert result.score == 0.0
    assert not result.passed


def test_unknown_items_do_not_improve_score() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("unknown",),
        ("a",),
    )

    assert result.score == 0.0


@pytest.mark.parametrize(
    "minimum_score",
    [-0.1, 1.1],
)
def test_invalid_reranker_threshold_is_rejected(
    minimum_score: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        RerankerEffectivenessEvaluator().evaluate(
            ("a",),
            ("a",),
            minimum_score=minimum_score,
        )


def test_blank_identifiers_are_ignored() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("a", "", "   "),
        ("a",),
    )

    assert result.actual_ids == ("a",)
    assert result.expected_ids == ("a",)
    assert result.score == 1.0


def test_custom_threshold_can_accept_partial_ranking() -> None:
    result = RerankerEffectivenessEvaluator().evaluate(
        ("a", "b"),
        ("a", "b"),
        minimum_score=0.5,
    )

    assert result.passed

