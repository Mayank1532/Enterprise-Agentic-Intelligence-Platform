"""Contracts for deterministic parallel batch execution."""

from dataclasses import dataclass

from enterprise_ai.core.batch_execution import BatchExecutionResult


@dataclass(frozen=True, slots=True)
class ParallelExecutionResult:
    """Deterministic aggregate result of parallel batch execution."""

    results: tuple[BatchExecutionResult, ...]
    total_processed: int
    total_skipped: int
    total_failed: int

    def __post_init__(self) -> None:
        """Validate aggregate execution invariants."""
        if self.total_processed < 0:
            raise ValueError("total_processed must not be negative.")

        if self.total_skipped < 0:
            raise ValueError("total_skipped must not be negative.")

        if self.total_failed < 0:
            raise ValueError("total_failed must not be negative.")

        total_items = sum(result.batch.size for result in self.results)

        if self.total_processed + self.total_skipped + self.total_failed != total_items:
            raise ValueError("aggregate execution counts must equal total batch size.")
