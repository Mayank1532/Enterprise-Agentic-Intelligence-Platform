"""Deterministic ingestion failure recovery contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RecoveryState(StrEnum):
    """Lifecycle state of a recoverable ingestion job."""

    RETRYABLE = "retryable"
    DEAD_LETTER = "dead_letter"


@dataclass(frozen=True, slots=True)
class RetryableJob:
    """A failed ingestion work item eligible for retry."""

    document_id: str
    content_hash: str
    attempt: int
    error: str

    def __post_init__(self) -> None:
        """Validate retryable job state."""
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not self.content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        if self.attempt < 1:
            raise ValueError("attempt must be at least 1.")

        if not self.error.strip():
            raise ValueError("error must not be empty.")

    @property
    def state(self) -> RecoveryState:
        """Return the current recovery state."""
        return RecoveryState.RETRYABLE


@dataclass(frozen=True, slots=True)
class DeadLetterJob:
    """A persistently failed ingestion work item."""

    document_id: str
    content_hash: str
    attempts: int
    error: str

    def __post_init__(self) -> None:
        """Validate dead-letter state."""
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not self.content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        if self.attempts < 1:
            raise ValueError("attempts must be at least 1.")

        if not self.error.strip():
            raise ValueError("error must not be empty.")

    @property
    def state(self) -> RecoveryState:
        """Return the terminal recovery state."""
        return RecoveryState.DEAD_LETTER


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Deterministic decision after an ingestion failure."""

    document_id: str
    content_hash: str
    attempt: int
    max_attempts: int
    error: str

    def __post_init__(self) -> None:
        """Validate recovery decision."""
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not self.content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        if self.attempt < 1:
            raise ValueError("attempt must be at least 1.")

        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot exceed max_attempts.")

        if not self.error.strip():
            raise ValueError("error must not be empty.")

    @property
    def should_retry(self) -> bool:
        """Return whether the failed job remains retryable."""
        return self.attempt < self.max_attempts

    def retry_job(self) -> RetryableJob:
        """Return a retryable representation."""
        if not self.should_retry:
            raise ValueError("job has exhausted its retry attempts.")

        return RetryableJob(
            document_id=self.document_id,
            content_hash=self.content_hash,
            attempt=self.attempt,
            error=self.error,
        )

    def dead_letter(self) -> DeadLetterJob:
        """Return a terminal dead-letter representation."""
        if self.should_retry:
            raise ValueError("job has remaining retry attempts.")

        return DeadLetterJob(
            document_id=self.document_id,
            content_hash=self.content_hash,
            attempts=self.attempt,
            error=self.error,
        )
