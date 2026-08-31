"""Deterministic batch planning for incremental ingestion."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.ingestion_state import DocumentState


class BatchIngestionPlanner:
    """Create deterministic ingestion batches."""

    def __init__(
        self,
        existing_state: Iterable[DocumentState] = (),
    ) -> None:
        """Initialize the planner."""
        self._engine = IncrementalIngestionEngine(existing_state)

    def plan(
        self,
        documents: Sequence[tuple[str, str]],
        batch_size: int,
    ) -> tuple[IngestionBatch, ...]:
        """Plan documents into deterministic batches."""
        if batch_size < 1:
            raise ValueError("batch_size must be positive.")

        decisions = tuple(
            self._engine.decide(
                document_id=document_id,
                content_hash=content_hash,
            )
            for document_id, content_hash in documents
        )

        return tuple(
            IngestionBatch(
                decisions=decisions[index : index + batch_size]
            )
            for index in range(0, len(decisions), batch_size)
        )
