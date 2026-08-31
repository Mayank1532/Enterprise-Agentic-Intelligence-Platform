"""Tests for benchmark domain contracts."""

import pytest

from enterprise_ai.core.benchmark import BenchmarkCase, BenchmarkDataset


def test_benchmark_case_is_constructed() -> None:
    case = BenchmarkCase(
        case_id="case-1",
        task="test task",
        expected_agent="retrieval",
        expected_tool="retrieval",
    )

    assert case.case_id == "case-1"
    assert case.expected_success is True


def test_benchmark_case_rejects_empty_case_id() -> None:
    with pytest.raises(ValueError, match="case_id"):
        BenchmarkCase(
            case_id="",
            task="test task",
            expected_agent="retrieval",
            expected_tool="retrieval",
        )


def test_benchmark_dataset_size() -> None:
    dataset = BenchmarkDataset(
        name="test",
        version="1.0",
        cases=(
            BenchmarkCase(
                case_id="case-1",
                task="task",
                expected_agent="retrieval",
                expected_tool="retrieval",
            ),
        ),
    )

    assert dataset.size == 1


def test_benchmark_dataset_rejects_duplicate_case_ids() -> None:
    case = BenchmarkCase(
        case_id="duplicate",
        task="task",
        expected_agent="retrieval",
        expected_tool="retrieval",
    )

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        BenchmarkDataset(
            name="test",
            version="1.0",
            cases=(case, case),
        )
