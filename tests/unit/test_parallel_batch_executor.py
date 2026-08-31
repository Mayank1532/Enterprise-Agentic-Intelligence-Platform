"""Tests for deterministic parallel batch execution."""

from enterprise_ai.common.batch_executor import BatchIngestionExecutor
from enterprise_ai.common.batch_ingestion import BatchIngestionPlanner
from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.common.parallel_batch_executor import (
    ParallelBatchExecutor,
)


def _build_batches():
    """Build deterministic planned batches."""
    planner = BatchIngestionPlanner()

    documents = (
        ("doc-001", "hash-001"),
        ("doc-002", "hash-002"),
        ("doc-003", "hash-003"),
        ("doc-004", "hash-004"),
    )

    return planner.plan(
        documents,
        batch_size=2,
    )


def _build_executor() -> ParallelBatchExecutor:
    """Build a parallel executor with a deterministic processor."""
    engine = IncrementalIngestionEngine()

    def processor(_: str) -> None:
        """Provide a deterministic no-op processor."""
        return None

    batch_executor = BatchIngestionExecutor(
        engine=engine,
        processor=processor,
    )

    return ParallelBatchExecutor(
        batch_executor,
        max_workers=2,
    )


def test_parallel_executor_processes_all_batches() -> None:
    """All CREATE decisions are processed."""
    executor = _build_executor()

    result = executor.execute(_build_batches())

    assert len(result.results) == 2
    assert result.total_processed == 4
    assert result.total_skipped == 0
    assert result.total_failed == 0


def test_parallel_executor_preserves_batch_order() -> None:
    """Parallel completion does not change input ordering."""
    executor = _build_executor()

    batches = _build_batches()
    result = executor.execute(batches)

    assert tuple(item.batch.decisions for item in result.results) == tuple(
        batch.decisions for batch in batches
    )


def test_parallel_executor_empty_input_is_safe() -> None:
    """Empty input produces an empty deterministic result."""
    executor = _build_executor()

    result = executor.execute(())

    assert result.results == ()
    assert result.total_processed == 0
    assert result.total_skipped == 0
    assert result.total_failed == 0


def test_parallel_executor_rejects_invalid_worker_count() -> None:
    """Worker count must be positive."""
    engine = IncrementalIngestionEngine()

    batch_executor = BatchIngestionExecutor(
        engine=engine,
        processor=lambda document_id: None,
    )

    try:
        ParallelBatchExecutor(
            batch_executor,
            max_workers=0,
        )
    except ValueError as exc:
        assert "max_workers" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_parallel_executor_is_deterministic() -> None:
    """Repeated execution produces the same result shape."""
    first_executor = _build_executor()
    second_executor = _build_executor()

    batches = _build_batches()

    first = first_executor.execute(batches)
    second = second_executor.execute(batches)

    assert first.total_processed == second.total_processed
    assert first.total_skipped == second.total_skipped
    assert first.total_failed == second.total_failed

    assert tuple(item.batch.decisions for item in first.results) == tuple(
        item.batch.decisions for item in second.results
    )
