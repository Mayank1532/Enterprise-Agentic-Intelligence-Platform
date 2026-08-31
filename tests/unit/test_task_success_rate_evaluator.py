"""Tests for task success rate evaluation."""

import pytest

from enterprise_ai.common.task_success_rate_evaluator import (
    TaskSuccessRateEvaluator,
)


def test_all_tasks_successful() -> None:
    evaluator = TaskSuccessRateEvaluator()

    assert evaluator.evaluate(
        (True, True, True, True)
    ) == 1.0


def test_partial_task_success() -> None:
    evaluator = TaskSuccessRateEvaluator()

    result = evaluator.evaluate(
        (True, False, True, False)
    )

    assert result == pytest.approx(0.5)


def test_no_tasks_returns_one() -> None:
    evaluator = TaskSuccessRateEvaluator()

    assert evaluator.evaluate(()) == 1.0
