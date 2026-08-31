"""Deterministic ingestion reporting contract."""

from __future__ import annotations

from dataclasses import dataclass

from enterprise_ai.core.ingestion_execution import IngestionExecutionResult


@dataclass(frozen=True, slots=True)
class IngestionReport:
    """Immutable summary of one ingestion execution."""

    planned_batches: int
    total_processed: int
    total_skipped: int
    total_failed: int

    @classmethod
    def from_execution(
        cls,
        result: IngestionExecutionResult,
    ) -> IngestionReport:
        """Build a report from an execution result."""
        return cls(
            planned_batches=result.planned_batches,
            total_processed=result.total_processed,
            total_skipped=result.total_skipped,
            total_failed=result.total_failed,
        )

    @property
    def total_documents(self) -> int:
        """Return total documents represented by the report."""
        return (
            self.total_processed
            + self.total_skipped
            + self.total_failed
        )

    @property
    def succeeded(self) -> bool:
        """Return whether the execution completed without failures."""
        return self.total_failed == 0

    @property
    def success_rate(self) -> float:
        """Return the fraction of documents processed or skipped."""
        if self.total_documents == 0:
            return 1.0

        return (
            self.total_processed + self.total_skipped
        ) / self.total_documents
