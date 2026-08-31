"""Deterministic end-to-end ingestion orchestration."""

from __future__ import annotations

from collections.abc import Sequence

from enterprise_ai.common.batch_ingestion import BatchIngestionPlanner
from enterprise_ai.common.parallel_batch_executor import ParallelBatchExecutor
from enterprise_ai.core.ingestion_execution import IngestionExecutionResult


class IngestionOrchestrator:
    """Plan and execute document ingestion deterministically."""

    def __init__(
        self,
        planner: BatchIngestionPlanner,
        executor: ParallelBatchExecutor,
    ) -> None:
        """Initialize the orchestrator."""
        self._planner = planner
        self._executor = executor

    def execute(
        self,
        documents: Sequence[tuple[str, str]],
        *,
        batch_size: int,
    ) -> IngestionExecutionResult:
        """Plan documents and execute the resulting batches."""
        batches = self._planner.plan(
            documents=documents,
            batch_size=batch_size,
        )

        execution = self._executor.execute(batches)

        return IngestionExecutionResult(
            planned_batches=len(batches),
            execution=execution,
        )
