"""Bounded ingestion queue service."""

from __future__ import annotations

from collections.abc import Iterable

from enterprise_ai.core.ingestion_queue import IngestionQueue


class IngestionQueueService:
    """Manage bounded ingestion work submission and consumption."""

    def __init__(self, *, capacity: int) -> None:
        """Initialize the queue service."""
        self._queue = IngestionQueue(capacity=capacity)

    @property
    def capacity(self) -> int:
        """Return queue capacity."""
        return self._queue.capacity

    @property
    def depth(self) -> int:
        """Return current queue depth."""
        return self._queue.depth

    @property
    def is_full(self) -> bool:
        """Return whether the queue is under backpressure."""
        return self._queue.is_full

    def submit(
        self,
        documents: Iterable[tuple[str, str]],
    ) -> int:
        """Submit work and return the resulting queue depth."""
        self._queue.enqueue_many(documents)
        return self.depth

    def next_item(self) -> tuple[str, str]:
        """Consume the oldest queued work item."""
        return self._queue.dequeue()

    def drain(self) -> tuple[tuple[str, str], ...]:
        """Consume all remaining queued work."""
        return self._queue.drain()
