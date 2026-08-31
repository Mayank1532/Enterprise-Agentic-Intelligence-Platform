"""Deterministic ingestion observability contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IngestionMetrics:
    """Immutable operational metrics for one ingestion execution."""

    queue_depth: int
    planned_batches: int
    processed: int
    skipped: int
    failed: int
    retryable: int
    dead_letter: int

    def __post_init__(self) -> None:
        """Validate metric values."""
        values = (
            self.queue_depth,
            self.planned_batches,
            self.processed,
            self.skipped,
            self.failed,
            self.retryable,
            self.dead_letter,
        )

        if any(value < 0 for value in values):
            raise ValueError("ingestion metrics must not be negative.")

    @property
    def total_documents(self) -> int:
        """Return total documents represented by execution metrics."""
        return self.processed + self.skipped + self.failed

    @property
    def successful_documents(self) -> int:
        """Return processed plus skipped documents."""
        return self.processed + self.skipped

    @property
    def success_rate(self) -> float:
        """Return successful document ratio."""
        if self.total_documents == 0:
            return 1.0

        return self.successful_documents / self.total_documents

    @property
    def failure_rate(self) -> float:
        """Return failed document ratio."""
        if self.total_documents == 0:
            return 0.0

        return self.failed / self.total_documents

    @property
    def has_failures(self) -> bool:
        """Return whether execution contains failures."""
        return self.failed > 0

    @property
    def has_recovery_work(self) -> bool:
        """Return whether retry or dead-letter work exists."""
        return self.retryable > 0 or self.dead_letter > 0
