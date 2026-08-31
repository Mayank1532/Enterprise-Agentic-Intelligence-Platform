"""Contracts for deterministic ingestion orchestration."""

from dataclasses import dataclass

from enterprise_ai.core.parallel_batch_execution import ParallelExecutionResult


@dataclass(frozen=True, slots=True)
class IngestionExecutionResult:
    """Deterministic result of an end-to-end ingestion execution."""

    planned_batches: int
    execution: ParallelExecutionResult

    def __post_init__(self) -> None:
        """Validate orchestration invariants."""
        if self.planned_batches < 0:
            raise ValueError("planned_batches must not be negative.")

        if self.planned_batches != len(self.execution.results):
            raise ValueError("planned_batches must equal executed batch count.")

    @property
    def total_processed(self) -> int:
        """Return total successfully processed documents."""
        return self.execution.total_processed

    @property
    def total_skipped(self) -> int:
        """Return total skipped documents."""
        return self.execution.total_skipped

    @property
    def total_failed(self) -> int:
        """Return total failed documents."""
        return self.execution.total_failed

    @property
    def total_documents(self) -> int:
        """Return total documents represented by the execution."""
        return self.total_processed + self.total_skipped + self.total_failed
