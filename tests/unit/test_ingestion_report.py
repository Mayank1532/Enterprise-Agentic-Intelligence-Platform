from enterprise_ai.core.ingestion_execution import (
    IngestionExecutionResult,
)
from enterprise_ai.core.ingestion_report import IngestionReport


def test_report_is_built_from_execution_result() -> None:
    result = IngestionExecutionResult(
        planned_batches=2,
        total_processed=3,
        total_skipped=2,
        total_failed=1,
    )

    report = IngestionReport.from_execution(result)

    assert report.planned_batches == 2
    assert report.total_processed == 3
    assert report.total_skipped == 2
    assert report.total_failed == 1


def test_report_total_documents_is_deterministic() -> None:
    result = IngestionExecutionResult(
        planned_batches=3,
        total_processed=4,
        total_skipped=3,
        total_failed=2,
    )

    report = IngestionReport.from_execution(result)

    assert report.total_documents == 9


def test_report_success_is_true_without_failures() -> None:
    result = IngestionExecutionResult(
        planned_batches=2,
        total_processed=4,
        total_skipped=3,
        total_failed=0,
    )

    report = IngestionReport.from_execution(result)

    assert report.succeeded is True
    assert report.success_rate == 1.0


def test_report_success_is_false_with_failures() -> None:
    result = IngestionExecutionResult(
        planned_batches=2,
        total_processed=4,
        total_skipped=2,
        total_failed=2,
    )

    report = IngestionReport.from_execution(result)

    assert report.succeeded is False
    assert report.success_rate == 0.75


def test_empty_report_has_perfect_success_rate() -> None:
    result = IngestionExecutionResult(
        planned_batches=0,
        total_processed=0,
        total_skipped=0,
        total_failed=0,
    )

    report = IngestionReport.from_execution(result)

    assert report.total_documents == 0
    assert report.success_rate == 1.0
