"""Tests for deterministic ingestion orchestration."""

from enterprise_ai.common.batch_executor import BatchIngestionExecutor
from enterprise_ai.common.batch_ingestion import BatchIngestionPlanner
from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.common.ingestion_orchestrator import IngestionOrchestrator
from enterprise_ai.common.parallel_batch_executor import (
    ParallelBatchExecutor,
)
from enterprise_ai.core.ingestion_execution import IngestionExecutionResult


def _build_orchestrator(
    calls: list[str],
) -> IngestionOrchestrator:
    """Build an orchestrator with deterministic dependencies."""
    planner = BatchIngestionPlanner()
    engine = IncrementalIngestionEngine()

    batch_executor = BatchIngestionExecutor(
        engine=engine,
        processor=calls.append,
    )

    parallel_executor = ParallelBatchExecutor(
        batch_executor,
        max_workers=2,
    )

    return IngestionOrchestrator(
        planner=planner,
        executor=parallel_executor,
    )


def test_orchestrator_executes_all_documents() -> None:
    """All new documents are processed."""
    calls: list[str] = []

    orchestrator = _build_orchestrator(calls)

    result = orchestrator.execute(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-3", "hash-3"),
            ("doc-4", "hash-4"),
        ),
        batch_size=2,
    )

    assert isinstance(result, IngestionExecutionResult)
    assert result.planned_batches == 2
    assert result.total_processed == 4
    assert result.total_skipped == 0
    assert result.total_failed == 0
    assert result.total_documents == 4
    assert calls == ["doc-1", "doc-2", "doc-3", "doc-4"]


def test_orchestrator_preserves_document_order() -> None:
    """Execution preserves the original batch/document ordering."""
    calls: list[str] = []

    orchestrator = _build_orchestrator(calls)

    orchestrator.execute(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-3", "hash-3"),
            ("doc-4", "hash-4"),
            ("doc-5", "hash-5"),
        ),
        batch_size=2,
    )

    assert calls == [
        "doc-1",
        "doc-2",
        "doc-3",
        "doc-4",
        "doc-5",
    ]


def test_orchestrator_handles_empty_input() -> None:
    """Empty input produces a deterministic empty result."""
    calls: list[str] = []

    orchestrator = _build_orchestrator(calls)

    result = orchestrator.execute(
        documents=(),
        batch_size=10,
    )

    assert result.planned_batches == 0
    assert result.total_processed == 0
    assert result.total_skipped == 0
    assert result.total_failed == 0
    assert result.total_documents == 0
    assert calls == []


def test_orchestrator_respects_incremental_skip_decisions() -> None:
    """Existing documents can be skipped by the planner state."""
    calls: list[str] = []

    planner = BatchIngestionPlanner(
        existing_state=(
            __import__(
                "enterprise_ai.core.ingestion_state",
                fromlist=["DocumentState"],
            ).DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=2,
            ),
        )
    )

    engine = IncrementalIngestionEngine(
        (
            __import__(
                "enterprise_ai.core.ingestion_state",
                fromlist=["DocumentState"],
            ).DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=2,
            ),
        )
    )

    batch_executor = BatchIngestionExecutor(
        engine=engine,
        processor=calls.append,
    )

    parallel_executor = ParallelBatchExecutor(
        batch_executor,
        max_workers=2,
    )

    orchestrator = IngestionOrchestrator(
        planner=planner,
        executor=parallel_executor,
    )

    result = orchestrator.execute(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
        ),
        batch_size=2,
    )

    assert result.planned_batches == 1
    assert result.total_processed == 1
    assert result.total_skipped == 1
    assert result.total_failed == 0
    assert result.total_documents == 2
    assert calls == ["doc-2"]


def test_ingestion_execution_result_rejects_invalid_batch_count() -> None:
    """Result rejects inconsistent planned batch counts."""
    from enterprise_ai.core.parallel_batch_execution import (
        ParallelExecutionResult,
    )

    execution = ParallelExecutionResult(
        results=(),
        total_processed=0,
        total_skipped=0,
        total_failed=0,
    )

    try:
        IngestionExecutionResult(
            planned_batches=1,
            execution=execution,
        )
    except ValueError as exc:
        assert "planned_batches" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_ingestion_execution_result_exposes_totals() -> None:
    """Convenience properties expose aggregate execution counts."""
    from enterprise_ai.core.parallel_batch_execution import (
        ParallelExecutionResult,
    )

    execution = ParallelExecutionResult(
        results=(),
        total_processed=0,
        total_skipped=0,
        total_failed=0,
    )

    result = IngestionExecutionResult(
        planned_batches=0,
        execution=execution,
    )

    assert result.total_processed == 0
    assert result.total_skipped == 0
    assert result.total_failed == 0
    assert result.total_documents == 0
