"""Tests for bounded ingestion queue behavior."""

import pytest

from enterprise_ai.common.ingestion_queue_service import (
    IngestionQueueService,
)
from enterprise_ai.core.ingestion_queue import IngestionQueue


def test_queue_starts_empty() -> None:
    queue = IngestionQueue(capacity=2)

    assert queue.capacity == 2
    assert queue.depth == 0
    assert queue.is_empty is True
    assert queue.is_full is False


def test_enqueue_preserves_fifo_order() -> None:
    queue = IngestionQueue(capacity=3)

    queue.enqueue("doc-1", "hash-1")
    queue.enqueue("doc-2", "hash-2")

    assert queue.dequeue() == ("doc-1", "hash-1")
    assert queue.dequeue() == ("doc-2", "hash-2")
    assert queue.is_empty is True


def test_queue_reaches_backpressure_at_capacity() -> None:
    queue = IngestionQueue(capacity=2)

    queue.enqueue("doc-1", "hash-1")
    queue.enqueue("doc-2", "hash-2")

    assert queue.depth == 2
    assert queue.is_full is True

    with pytest.raises(OverflowError, match="capacity exceeded"):
        queue.enqueue("doc-3", "hash-3")


def test_enqueue_many_is_atomic_when_capacity_is_insufficient() -> None:
    queue = IngestionQueue(capacity=2)

    queue.enqueue("doc-1", "hash-1")

    with pytest.raises(OverflowError, match="capacity exceeded"):
        queue.enqueue_many(
            (
                ("doc-2", "hash-2"),
                ("doc-3", "hash-3"),
            )
        )

    assert queue.depth == 1
    assert queue.dequeue() == ("doc-1", "hash-1")


def test_drain_returns_fifo_items_and_clears_queue() -> None:
    queue = IngestionQueue(capacity=3)

    queue.enqueue_many(
        (
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-3", "hash-3"),
        )
    )

    assert queue.drain() == (
        ("doc-1", "hash-1"),
        ("doc-2", "hash-2"),
        ("doc-3", "hash-3"),
    )

    assert queue.depth == 0
    assert queue.is_empty is True


def test_queue_rejects_invalid_capacity() -> None:
    with pytest.raises(ValueError, match="capacity must be positive"):
        IngestionQueue(capacity=0)


@pytest.mark.parametrize(
    "document_id,content_hash",
    (
        ("", "hash"),
        ("   ", "hash"),
        ("doc", ""),
        ("doc", "   "),
    ),
)
def test_queue_rejects_invalid_work_item(
    document_id: str,
    content_hash: str,
) -> None:
    queue = IngestionQueue(capacity=2)

    with pytest.raises(ValueError):
        queue.enqueue(document_id, content_hash)


def test_queue_service_exposes_backpressure_state() -> None:
    service = IngestionQueueService(capacity=2)

    depth = service.submit(
        (
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
        )
    )

    assert depth == 2
    assert service.depth == 2
    assert service.capacity == 2
    assert service.is_full is True


def test_queue_service_consumes_fifo_work() -> None:
    service = IngestionQueueService(capacity=2)

    service.submit(
        (
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
        )
    )

    assert service.next_item() == ("doc-1", "hash-1")
    assert service.next_item() == ("doc-2", "hash-2")
    assert service.depth == 0
