from enterprise_ai.core.batch_execution import BatchExecutionResult
from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.ingestion_execution import IngestionExecutionResult
from enterprise_ai.core.ingestion_report import IngestionReport
from enterprise_ai.core.ingestion_state import (
    IngestionAction,
    IngestionDecision,
)
from enterprise_ai.core.parallel_batch_execution import (
    ParallelExecutionResult,
)


def _make_execution_result(
    processed: int,
    skipped: int,
    failed: int,
) -> IngestionExecutionResult:
    """Build a valid execution result using the production contracts."""
    total = processed + skipped + failed

    decisions = tuple(
        IngestionDecision(
            action=IngestionAction.CREATE,
            document_id=f"doc-{index}",
            previous_version=None,
            new_version=1,
        )
        for index in range(total)
    )

    if total == 0:
        execution = ParallelExecutionResult(
            results=(),
            total_processed=0,
            total_skipped=0,
            total_failed=0,
        )

        return IngestionExecutionResult(
            planned_batches=0,
            execution=execution,
        )

    batch = IngestionBatch(decisions=decisions)

    batch_result = BatchExecutionResult(
        batch=batch,
        processed=processed,
        skipped=skipped,
        failed=failed,
    )

    execution = ParallelExecutionResult(
        results=(batch_result,),
        total_processed=processed,
        total_skipped=skipped,
        total_failed=failed,
    )

    return IngestionExecutionResult(
        planned_batches=1,
        execution=execution,
    )


def test_report_is_built_from_execution_result() -> None:
    """Report exposes the aggregate execution counts."""
    result = _make_execution_result(
        processed=3,
        skipped=2,
        failed=1,
    )

    report = IngestionReport.from_execution(result)

    assert report.planned_batches == 1
    assert report.total_processed == 3
    assert report.total_skipped == 2
    assert report.total_failed == 1


def test_report_total_documents_is_deterministic() -> None:
    """Report calculates total represented documents."""
    result = _make_execution_result(
        processed=4,
        skipped=3,
        failed=2,
    )

    report = IngestionReport.from_execution(result)

    assert report.total_documents == 9


def test_report_success_is_true_without_failures() -> None:
    """Execution with no failures is successful."""
    result = _make_execution_result(
        processed=4,
        skipped=3,
        failed=0,
    )

    report = IngestionReport.from_execution(result)

    assert report.succeeded is True
    assert report.success_rate == 1.0


def test_report_success_is_false_with_failures() -> None:
    """Execution containing failures is not successful."""
    result = _make_execution_result(
        processed=4,
        skipped=2,
        failed=2,
    )

    report = IngestionReport.from_execution(result)

    assert report.succeeded is False
    assert report.success_rate == 0.75


def test_empty_report_has_perfect_success_rate() -> None:
    """Empty execution has a deterministic perfect success rate."""
    result = _make_execution_result(
        processed=0,
        skipped=0,
        failed=0,
    )

    report = IngestionReport.from_execution(result)

    assert report.planned_batches == 0
    assert report.total_documents == 0
    assert report.success_rate == 1.0
