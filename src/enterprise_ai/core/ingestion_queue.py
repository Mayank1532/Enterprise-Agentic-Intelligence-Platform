"""Bounded ingestion work queue contract."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable


class IngestionQueue:
    """Deterministic bounded FIFO queue for ingestion work."""

    def __init__(self, *, capacity: int) -> None:
        """Initialize a bounded queue."""
        if capacity < 1:
            raise ValueError("capacity must be positive.")

        self._capacity = capacity
        self._items: deque[tuple[str, str]] = deque()

    @property
    def capacity(self) -> int:
        """Return maximum queue capacity."""
        return self._capacity

    @property
    def depth(self) -> int:
        """Return current queue depth."""
        return len(self._items)

    @property
    def is_full(self) -> bool:
        """Return whether the queue has reached capacity."""
        return self.depth >= self.capacity

    @property
    def is_empty(self) -> bool:
        """Return whether the queue contains no work."""
        return not self._items

    def enqueue(self, document_id: str, content_hash: str) -> None:
        """Add one document work item to the queue."""
        if not document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        if self.is_full:
            raise OverflowError("ingestion queue capacity exceeded.")

        self._items.append((document_id, content_hash))

    def enqueue_many(
        self,
        documents: Iterable[tuple[str, str]],
    ) -> None:
        """Add multiple work items while preserving input order."""
        items = tuple(documents)

        if self.depth + len(items) > self.capacity:
            raise OverflowError("ingestion queue capacity exceeded.")

        for document_id, content_hash in items:
            if not document_id.strip():
                raise ValueError("document_id must not be empty.")

            if not content_hash.strip():
                raise ValueError("content_hash must not be empty.")

        self._items.extend(items)

    def dequeue(self) -> tuple[str, str]:
        """Remove and return the oldest work item."""
        if self.is_empty:
            raise IndexError("cannot dequeue from an empty queue.")

        return self._items.popleft()

    def drain(self) -> tuple[tuple[str, str], ...]:
        """Remove and return all queued work in FIFO order."""
        items = tuple(self._items)
        self._items.clear()
        return items
