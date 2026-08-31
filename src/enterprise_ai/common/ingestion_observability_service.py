"""Deterministic ingestion observability service."""

from __future__ import annotations

from enterprise_ai.core.ingestion_observability import IngestionMetrics


class IngestionObservabilityService:
    """Record and expose the latest ingestion operational metrics."""

    def __init__(self) -> None:
        """Initialize an empty observability service."""
        self._latest: IngestionMetrics | None = None

    @property
    def latest(self) -> IngestionMetrics | None:
        """Return the latest recorded metrics."""
        return self._latest

    def record(
        self,
        metrics: IngestionMetrics,
    ) -> IngestionMetrics:
        """Record and return one immutable metrics snapshot."""
        self._latest = metrics
        return metrics

    def snapshot(self) -> IngestionMetrics | None:
        """Return the current metrics snapshot."""
        return self._latest

    def reset(self) -> None:
        """Clear the current metrics snapshot."""
        self._latest = None
