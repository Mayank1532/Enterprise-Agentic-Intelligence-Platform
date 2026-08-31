"""Tests for benchmark regression evaluation."""

import pytest

from enterprise_ai.common.benchmark_regression_evaluator import (
    BenchmarkRegressionEvaluator,
)
from enterprise_ai.core.benchmark import BenchmarkCase, BenchmarkDataset


@pytest.fixture
def dataset() -> BenchmarkDataset:
    return BenchmarkDataset(
        name="test-benchmark",
        version="1.0",
        cases=(
            BenchmarkCase(
                case_id="case-1",
                task="retrieve",
                expected_agent="retrieval",
                expected_tool="retrieval",
            ),
            BenchmarkCase(
                case_id="case-2",
                task="live",
                expected_agent="live_data",
                expected_tool="live_data",
            ),
            BenchmarkCase(
                case_id="case-3",
                task="mcp",
                expected_agent="mcp",
                expected_tool="mcp",
            ),
            BenchmarkCase(
                case_id="case-4",
                task="a2a",
                expected_agent="a2a",
                expected_tool="a2a",
            ),
        ),
    )


def test_all_cases_pass(dataset: BenchmarkDataset) -> None:
    evaluator = BenchmarkRegressionEvaluator()

    result = evaluator.evaluate(
        dataset=dataset,
        actual_agents=(
            "retrieval",
            "live_data",
            "mcp",
            "a2a",
        ),
        actual_tools=(
            "retrieval",
            "live_data",
            "mcp",
            "a2a",
        ),
        actual_success=(True, True, True, True),
    )

    assert result.total_cases == 4
    assert result.passed_cases == 4
    assert result.failed_cases == 0
    assert result.pass_rate == 1.0


def test_partial_regression_failure(dataset: BenchmarkDataset) -> None:
    evaluator = BenchmarkRegressionEvaluator()

    result = evaluator.evaluate(
        dataset=dataset,
        actual_agents=(
            "retrieval",
            "wrong_agent",
            "mcp",
            "a2a",
        ),
        actual_tools=(
            "retrieval",
            "wrong_tool",
            "mcp",
            "a2a",
        ),
        actual_success=(True, True, True, False),
    )

    assert result.total_cases == 4
    assert result.passed_cases == 2
    assert result.failed_cases == 2
    assert result.pass_rate == pytest.approx(0.5)


def test_result_collections_must_match_dataset(
    dataset: BenchmarkDataset,
) -> None:
    evaluator = BenchmarkRegressionEvaluator()

    with pytest.raises(
        ValueError,
        match="match dataset size",
    ):
        evaluator.evaluate(
            dataset=dataset,
            actual_agents=("retrieval",),
            actual_tools=("retrieval",),
            actual_success=(True,),
        )


def test_empty_dataset_is_perfect() -> None:
    dataset = BenchmarkDataset(
        name="empty",
        version="1.0",
        cases=(),
    )

    evaluator = BenchmarkRegressionEvaluator()

    result = evaluator.evaluate(
        dataset=dataset,
        actual_agents=(),
        actual_tools=(),
        actual_success=(),
    )

    assert result.total_cases == 0
    assert result.passed_cases == 0
    assert result.failed_cases == 0
    assert result.pass_rate == 1.0
