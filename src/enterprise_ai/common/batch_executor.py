"""Deterministic batch ingestion execution."""

from __future__ import annotations

from collections.abc import Callable

from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.core.batch_execution import BatchExecutionResult
from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.ingestion_state import IngestionAction


class BatchIngestionExecutor:
    """Execute planned ingestion batches deterministically."""

    def __init__(
        self,
        engine: IncrementalIngestionEngine,
        processor: Callable[[str], None],
    ) -> None:
        """Initialize the executor."""
        self._engine = engine
        self._processor = processor

    def execute(
        self,
        batch: IngestionBatch,
    ) -> BatchExecutionResult:
        """Execute a batch while preserving deterministic ordering."""
        processed = 0
        skipped = 0
        failed = 0

        for decision in batch.decisions:
            if decision.action is IngestionAction.SKIP:
                skipped += 1
                continue

            state = self._engine.get_state(decision.document_id)

            if state is None and decision.action is IngestionAction.UPDATE:
                failed += 1
                continue

            try:
                self._processor(decision.document_id)
            except Exception:
                failed += 1
                continue

            if decision.action is IngestionAction.CREATE:
                self._engine.apply(
                    document_id=decision.document_id,
                    content_hash=f"processed:{decision.document_id}",
                )
            elif decision.action is IngestionAction.UPDATE:
                if state is None:
                    failed += 1
                    continue

                self._engine.apply(
                    document_id=decision.document_id,
                    content_hash=f"processed:{decision.document_id}",
                )

            processed += 1

        return BatchExecutionResult(
            batch=batch,
            processed=processed,
            skipped=skipped,
            failed=failed,
        )
