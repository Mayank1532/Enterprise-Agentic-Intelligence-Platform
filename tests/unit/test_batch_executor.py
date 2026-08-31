"""Tests for deterministic batch ingestion execution."""

from enterprise_ai.common.batch_executor import BatchIngestionExecutor
from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.ingestion_state import (
    DocumentState,
    IngestionAction,
    IngestionDecision,
)


def test_executor_processes_create_decision() -> None:
    engine = IncrementalIngestionEngine()

    calls: list[str] = []

    executor = BatchIngestionExecutor(
        engine=engine,
        processor=calls.append,
    )

    batch = IngestionBatch(
        decisions=(
            IngestionDecision(
                action=IngestionAction.CREATE,
                document_id="doc-1",
                previous_version=None,
                new_version=1,
            ),
        )
    )

    result = executor.execute(batch)

    assert result.processed == 1
    assert result.skipped == 0
    assert result.failed == 0
    assert calls == ["doc-1"]


def test_executor_skips_skip_decisions() -> None:
    engine = IncrementalIngestionEngine(
        (
            DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=2,
            ),
        )
    )

    calls: list[str] = []

    executor = BatchIngestionExecutor(
        engine=engine,
        processor=calls.append,
    )

    batch = IngestionBatch(
        decisions=(
            IngestionDecision(
                action=IngestionAction.SKIP,
                document_id="doc-1",
                previous_version=2,
                new_version=None,
            ),
        )
    )

    result = executor.execute(batch)

    assert result.processed == 0
    assert result.skipped == 1
    assert result.failed == 0
    assert calls == []


def test_executor_processes_multiple_decisions_in_order() -> None:
    engine = IncrementalIngestionEngine()

    calls: list[str] = []

    executor = BatchIngestionExecutor(
        engine=engine,
        processor=calls.append,
    )

    batch = IngestionBatch(
        decisions=(
            IngestionDecision(
                action=IngestionAction.CREATE,
                document_id="doc-1",
                previous_version=None,
                new_version=1,
            ),
            IngestionDecision(
                action=IngestionAction.CREATE,
                document_id="doc-2",
                previous_version=None,
                new_version=1,
            ),
        )
    )

    result = executor.execute(batch)

    assert result.processed == 2
    assert result.skipped == 0
    assert result.failed == 0
    assert calls == ["doc-1", "doc-2"]


def test_executor_counts_processor_failure() -> None:
    engine = IncrementalIngestionEngine()

    def processor(_: str) -> None:
        raise RuntimeError("processing failed")

    executor = BatchIngestionExecutor(
        engine=engine,
        processor=processor,
    )

    batch = IngestionBatch(
        decisions=(
            IngestionDecision(
                action=IngestionAction.CREATE,
                document_id="doc-1",
                previous_version=None,
                new_version=1,
            ),
        )
    )

    result = executor.execute(batch)

    assert result.processed == 0
    assert result.skipped == 0
    assert result.failed == 1
