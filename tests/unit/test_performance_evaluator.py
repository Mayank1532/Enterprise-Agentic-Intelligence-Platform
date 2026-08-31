"""Tests for latency, throughput, and failure-rate evaluation."""

import pytest

from enterprise_ai.common.performance_evaluator import PerformanceEvaluator


def test_mean_latency() -> None:
    evaluator = PerformanceEvaluator()

    assert evaluator.latency(
        (1.0, 2.0, 3.0, 4.0)
    ) == pytest.approx(2.5)


def test_empty_latency_returns_zero() -> None:
    evaluator = PerformanceEvaluator()

    assert evaluator.latency(()) == 0.0


def test_negative_latency_is_rejected() -> None:
    evaluator = PerformanceEvaluator()

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        evaluator.latency((1.0, -1.0))


def test_throughput() -> None:
    evaluator = PerformanceEvaluator()

    assert evaluator.throughput(
        completed_items=100,
        duration_seconds=20.0,
    ) == pytest.approx(5.0)


def test_invalid_throughput_duration_is_rejected() -> None:
    evaluator = PerformanceEvaluator()

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        evaluator.throughput(
            completed_items=10,
            duration_seconds=0.0,
        )


def test_failure_rate() -> None:
    evaluator = PerformanceEvaluator()

    assert evaluator.failure_rate(
        failed_items=2,
        total_items=10,
    ) == pytest.approx(0.2)


def test_zero_total_failure_rate() -> None:
    evaluator = PerformanceEvaluator()

    assert evaluator.failure_rate(
        failed_items=0,
        total_items=0,
    ) == 0.0


def test_failure_count_cannot_exceed_total() -> None:
    evaluator = PerformanceEvaluator()

    with pytest.raises(
        ValueError,
        match="exceed total",
    ):
        evaluator.failure_rate(
            failed_items=11,
            total_items=10,
        )
