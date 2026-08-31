"""Deterministic parallel batch ingestion execution."""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from enterprise_ai.common.batch_executor import BatchIngestionExecutor
from enterprise_ai.core.batch_execution import BatchExecutionResult
from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.parallel_batch_execution import (
    ParallelExecutionResult,
)


class ParallelBatchExecutor:
    """Execute planned ingestion batches concurrently."""

    def __init__(
        self,
        executor: BatchIngestionExecutor,
        *,
        max_workers: int = 4,
    ) -> None:
        """Initialize the parallel executor."""
        if max_workers <= 0:
            raise ValueError("max_workers must be positive.")

        self._executor = executor
        self._max_workers = max_workers

    def execute(
        self,
        batches: Sequence[IngestionBatch],
    ) -> ParallelExecutionResult:
        """Execute batches concurrently while preserving batch order."""
        if not batches:
            return ParallelExecutionResult(
                results=(),
                total_processed=0,
                total_skipped=0,
                total_failed=0,
            )

        with ThreadPoolExecutor(
            max_workers=self._max_workers,
        ) as pool:
            futures = [
                pool.submit(
                    self._executor.execute,
                    batch,
                )
                for batch in batches
            ]

            results: tuple[BatchExecutionResult, ...] = tuple(future.result() for future in futures)

        return ParallelExecutionResult(
            results=results,
            total_processed=sum(result.processed for result in results),
            total_skipped=sum(result.skipped for result in results),
            total_failed=sum(result.failed for result in results),
        )
