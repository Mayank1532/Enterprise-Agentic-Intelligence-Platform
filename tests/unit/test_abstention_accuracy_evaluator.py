"""Tests for abstention accuracy evaluation."""

import pytest

from enterprise_ai.common.abstention_accuracy_evaluator import (
    AbstentionAccuracyEvaluator,
)


def test_all_abstention_decisions_correct() -> None:
    evaluator = AbstentionAccuracyEvaluator()

    result = evaluator.evaluate(
        expected_abstentions=(True, False, True, False),
        actual_abstentions=(True, False, True, False),
    )

    assert result == 1.0


def test_partial_abstention_accuracy() -> None:
    evaluator = AbstentionAccuracyEvaluator()

    result = evaluator.evaluate(
        expected_abstentions=(True, False, True, False),
        actual_abstentions=(True, True, False, False),
    )

    assert result == pytest.approx(0.5)


def test_empty_inputs_are_perfectly_accurate() -> None:
    evaluator = AbstentionAccuracyEvaluator()

    assert evaluator.evaluate((), ()) == 1.0


def test_length_mismatch_is_rejected() -> None:
    evaluator = AbstentionAccuracyEvaluator()

    with pytest.raises(
        ValueError,
        match="equal length",
    ):
        evaluator.evaluate(
            expected_abstentions=(True,),
            actual_abstentions=(),
        )
