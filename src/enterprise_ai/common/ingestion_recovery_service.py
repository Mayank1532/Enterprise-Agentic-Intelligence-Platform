"""Deterministic ingestion failure recovery service."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from enterprise_ai.core.ingestion_recovery import (
    DeadLetterJob,
    RecoveryDecision,
    RetryableJob,
)


class IngestionRecoveryService:
    """Track retryable failures and persistent dead-letter failures."""

    def __init__(self, *, max_attempts: int) -> None:
        """Initialize the recovery service."""
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        self._max_attempts = max_attempts
        self._retryable: deque[RetryableJob] = deque()
        self._dead_letters: list[DeadLetterJob] = []

    @property
    def max_attempts(self) -> int:
        """Return configured maximum attempts."""
        return self._max_attempts

    @property
    def retry_depth(self) -> int:
        """Return number of queued retryable jobs."""
        return len(self._retryable)

    @property
    def dead_letter_count(self) -> int:
        """Return number of terminal dead-letter jobs."""
        return len(self._dead_letters)

    def record_failure(
        self,
        *,
        document_id: str,
        content_hash: str,
        attempt: int,
        error: str,
    ) -> RecoveryDecision:
        """Record a failure and classify it deterministically."""
        decision = RecoveryDecision(
            document_id=document_id,
            content_hash=content_hash,
            attempt=attempt,
            max_attempts=self.max_attempts,
            error=error,
        )

        if decision.should_retry:
            self._retryable.append(decision.retry_job())
        else:
            self._dead_letters.append(decision.dead_letter())

        return decision

    def next_retry(self) -> RetryableJob:
        """Return the oldest retryable job."""
        if not self._retryable:
            raise IndexError("no retryable jobs available.")

        return self._retryable.popleft()

    def retry_jobs(self) -> tuple[RetryableJob, ...]:
        """Return queued retryable jobs without mutating the queue."""
        return tuple(self._retryable)

    def dead_letters(self) -> tuple[DeadLetterJob, ...]:
        """Return all dead-letter jobs."""
        return tuple(self._dead_letters)

    def recover_many(
        self,
        failures: Iterable[tuple[str, str, int, str]],
    ) -> tuple[RecoveryDecision, ...]:
        """Classify multiple failures in deterministic input order."""
        return tuple(
            self.record_failure(
                document_id=document_id,
                content_hash=content_hash,
                attempt=attempt,
                error=error,
            )
            for document_id, content_hash, attempt, error in failures
        )
