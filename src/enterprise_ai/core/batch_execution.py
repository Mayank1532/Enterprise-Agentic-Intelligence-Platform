"""Contracts for deterministic batch ingestion execution."""

from dataclasses import dataclass

from enterprise_ai.core.ingestion_batch import IngestionBatch


@dataclass(frozen=True, slots=True)
class BatchExecutionResult:
    """Deterministic result of executing an ingestion batch."""

    batch: IngestionBatch
    processed: int
    skipped: int
    failed: int

    def __post_init__(self) -> None:
        """Validate execution result invariants."""
        if self.processed < 0:
            raise ValueError("processed must not be negative.")

        if self.skipped < 0:
            raise ValueError("skipped must not be negative.")

        if self.failed < 0:
            raise ValueError("failed must not be negative.")

        if self.processed + self.skipped + self.failed != self.batch.size:
            raise ValueError(
                "execution counts must equal batch size."
            )
