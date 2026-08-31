"""Tests for deterministic ingestion failure recovery."""

import pytest

from enterprise_ai.common.ingestion_recovery_service import (
    IngestionRecoveryService,
)
from enterprise_ai.core.ingestion_recovery import (
    DeadLetterJob,
    RecoveryDecision,
    RecoveryState,
    RetryableJob,
)


def test_recovery_decision_is_retryable_before_max_attempts() -> None:
    decision = RecoveryDecision(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=1,
        max_attempts=3,
        error="temporary failure",
    )

    assert decision.should_retry is True
    assert decision.retry_job() == RetryableJob(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=1,
        error="temporary failure",
    )


def test_recovery_decision_becomes_dead_letter_at_max_attempts() -> None:
    decision = RecoveryDecision(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=3,
        max_attempts=3,
        error="persistent failure",
    )

    assert decision.should_retry is False
    assert decision.dead_letter() == DeadLetterJob(
        document_id="doc-1",
        content_hash="hash-1",
        attempts=3,
        error="persistent failure",
    )


def test_retry_job_cannot_be_created_after_max_attempts() -> None:
    decision = RecoveryDecision(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=2,
        max_attempts=2,
        error="persistent failure",
    )

    with pytest.raises(
        ValueError,
        match="exhausted its retry attempts",
    ):
        decision.retry_job()


def test_dead_letter_cannot_be_created_before_max_attempts() -> None:
    decision = RecoveryDecision(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=1,
        max_attempts=2,
        error="temporary failure",
    )

    with pytest.raises(
        ValueError,
        match="remaining retry attempts",
    ):
        decision.dead_letter()


def test_service_queues_retryable_failure() -> None:
    service = IngestionRecoveryService(max_attempts=3)

    decision = service.record_failure(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=1,
        error="temporary failure",
    )

    assert decision.should_retry is True
    assert service.retry_depth == 1
    assert service.dead_letter_count == 0
    assert service.next_retry().document_id == "doc-1"
    assert service.retry_depth == 0


def test_service_moves_persistent_failure_to_dead_letter() -> None:
    service = IngestionRecoveryService(max_attempts=3)

    decision = service.record_failure(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=3,
        error="persistent failure",
    )

    assert decision.should_retry is False
    assert service.retry_depth == 0
    assert service.dead_letter_count == 1

    dead_letter = service.dead_letters()[0]

    assert dead_letter.document_id == "doc-1"
    assert dead_letter.attempts == 3
    assert dead_letter.state == RecoveryState.DEAD_LETTER


def test_service_preserves_retry_fifo_order() -> None:
    service = IngestionRecoveryService(max_attempts=3)

    service.record_failure(
        document_id="doc-1",
        content_hash="hash-1",
        attempt=1,
        error="failure-1",
    )
    service.record_failure(
        document_id="doc-2",
        content_hash="hash-2",
        attempt=2,
        error="failure-2",
    )

    assert service.next_retry().document_id == "doc-1"
    assert service.next_retry().document_id == "doc-2"


def test_service_rejects_invalid_max_attempts() -> None:
    with pytest.raises(
        ValueError,
        match="max_attempts must be at least 1",
    ):
        IngestionRecoveryService(max_attempts=0)


def test_service_rejects_empty_retry_queue_consumption() -> None:
    service = IngestionRecoveryService(max_attempts=2)

    with pytest.raises(
        IndexError,
        match="no retryable jobs available",
    ):
        service.next_retry()


def test_recover_many_preserves_order_and_classifies_failures() -> None:
    service = IngestionRecoveryService(max_attempts=2)

    decisions = service.recover_many(
        (
            ("doc-1", "hash-1", 1, "temporary"),
            ("doc-2", "hash-2", 2, "persistent"),
            ("doc-3", "hash-3", 1, "temporary"),
        )
    )

    assert len(decisions) == 3
    assert decisions[0].should_retry is True
    assert decisions[1].should_retry is False
    assert decisions[2].should_retry is True

    assert service.retry_depth == 2
    assert service.dead_letter_count == 1


@pytest.mark.parametrize(
    "document_id,content_hash,attempt,error",
    (
        ("", "hash", 1, "error"),
        ("doc", "", 1, "error"),
        ("doc", "hash", 0, "error"),
        ("doc", "hash", 1, ""),
    ),
)
def test_recovery_decision_rejects_invalid_values(
    document_id: str,
    content_hash: str,
    attempt: int,
    error: str,
) -> None:
    with pytest.raises(ValueError):
        RecoveryDecision(
            document_id=document_id,
            content_hash=content_hash,
            attempt=attempt,
            max_attempts=2,
            error=error,
        )
