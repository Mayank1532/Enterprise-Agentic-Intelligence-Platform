"""Tests for deterministic ingestion observability."""

import pytest

from enterprise_ai.common.ingestion_observability_service import (
    IngestionObservabilityService,
)
from enterprise_ai.core.ingestion_observability import IngestionMetrics


def test_metrics_capture_operational_counts() -> None:
    metrics = IngestionMetrics(
        queue_depth=4,
        planned_batches=3,
        processed=7,
        skipped=2,
        failed=1,
        retryable=1,
        dead_letter=0,
    )

    assert metrics.queue_depth == 4
    assert metrics.planned_batches == 3
    assert metrics.processed == 7
    assert metrics.skipped == 2
    assert metrics.failed == 1
    assert metrics.retryable == 1
    assert metrics.dead_letter == 0


def test_metrics_calculate_total_documents() -> None:
    metrics = IngestionMetrics(
        queue_depth=0,
        planned_batches=2,
        processed=6,
        skipped=3,
        failed=1,
        retryable=0,
        dead_letter=0,
    )

    assert metrics.total_documents == 10
    assert metrics.successful_documents == 9


def test_metrics_calculate_success_and_failure_rates() -> None:
    metrics = IngestionMetrics(
        queue_depth=0,
        planned_batches=1,
        processed=6,
        skipped=2,
        failed=2,
        retryable=1,
        dead_letter=1,
    )

    assert metrics.success_rate == 0.8
    assert metrics.failure_rate == 0.2


def test_empty_metrics_have_deterministic_rates() -> None:
    metrics = IngestionMetrics(
        queue_depth=0,
        planned_batches=0,
        processed=0,
        skipped=0,
        failed=0,
        retryable=0,
        dead_letter=0,
    )

    assert metrics.total_documents == 0
    assert metrics.success_rate == 1.0
    assert metrics.failure_rate == 0.0


def test_metrics_detect_failures() -> None:
    metrics = IngestionMetrics(
        queue_depth=1,
        planned_batches=1,
        processed=2,
        skipped=0,
        failed=1,
        retryable=1,
        dead_letter=0,
    )

    assert metrics.has_failures is True
    assert metrics.has_recovery_work is True


def test_metrics_detect_dead_letter_recovery_work() -> None:
    metrics = IngestionMetrics(
        queue_depth=0,
        planned_batches=1,
        processed=2,
        skipped=1,
        failed=1,
        retryable=0,
        dead_letter=1,
    )

    assert metrics.has_recovery_work is True


def test_metrics_with_no_failures_have_no_failure_state() -> None:
    metrics = IngestionMetrics(
        queue_depth=0,
        planned_batches=1,
        processed=3,
        skipped=2,
        failed=0,
        retryable=0,
        dead_letter=0,
    )

    assert metrics.has_failures is False
    assert metrics.has_recovery_work is False


def test_negative_metrics_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        IngestionMetrics(
            queue_depth=-1,
            planned_batches=0,
            processed=0,
            skipped=0,
            failed=0,
            retryable=0,
            dead_letter=0,
        )


def test_observability_service_starts_empty() -> None:
    service = IngestionObservabilityService()

    assert service.latest is None
    assert service.snapshot() is None


def test_observability_service_records_latest_snapshot() -> None:
    service = IngestionObservabilityService()

    metrics = IngestionMetrics(
        queue_depth=3,
        planned_batches=2,
        processed=5,
        skipped=1,
        failed=1,
        retryable=1,
        dead_letter=0,
    )

    recorded = service.record(metrics)

    assert recorded == metrics
    assert service.latest == metrics
    assert service.snapshot() == metrics


def test_observability_service_replaces_previous_snapshot() -> None:
    service = IngestionObservabilityService()

    first = IngestionMetrics(
        queue_depth=2,
        planned_batches=1,
        processed=2,
        skipped=0,
        failed=0,
        retryable=0,
        dead_letter=0,
    )

    second = IngestionMetrics(
        queue_depth=0,
        planned_batches=2,
        processed=5,
        skipped=1,
        failed=1,
        retryable=0,
        dead_letter=1,
    )

    service.record(first)
    service.record(second)

    assert service.latest == second


def test_observability_service_can_reset() -> None:
    service = IngestionObservabilityService()

    metrics = IngestionMetrics(
        queue_depth=1,
        planned_batches=1,
        processed=1,
        skipped=0,
        failed=0,
        retryable=0,
        dead_letter=0,
    )

    service.record(metrics)
    service.reset()

    assert service.latest is None
