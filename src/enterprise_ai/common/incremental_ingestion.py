"""Deterministic incremental ingestion decision engine."""

from __future__ import annotations

from collections.abc import Iterable

from enterprise_ai.core.ingestion_state import (
    DocumentState,
    IngestionAction,
    IngestionDecision,
)


class IncrementalIngestionEngine:
    """Determine whether incoming documents require processing."""

    def __init__(
        self,
        existing_state: Iterable[DocumentState] = (),
    ) -> None:
        """Initialize the engine with known document state."""
        self._state: dict[str, DocumentState] = {
            item.document_id: item for item in existing_state
        }

    def decide(
        self,
        document_id: str,
        content_hash: str,
    ) -> IngestionDecision:
        """Return a deterministic create/update/skip decision."""
        if not document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        existing = self._state.get(document_id)

        if existing is None:
            return IngestionDecision(
                action=IngestionAction.CREATE,
                document_id=document_id,
                previous_version=None,
                new_version=1,
            )

        if existing.content_hash == content_hash:
            return IngestionDecision(
                action=IngestionAction.SKIP,
                document_id=document_id,
                previous_version=existing.version,
                new_version=None,
            )

        return IngestionDecision(
            action=IngestionAction.UPDATE,
            document_id=document_id,
            previous_version=existing.version,
            new_version=existing.version + 1,
        )

    def apply(
        self,
        document_id: str,
        content_hash: str,
    ) -> IngestionDecision:
        """Apply the deterministic ingestion decision."""
        decision = self.decide(
            document_id=document_id,
            content_hash=content_hash,
        )

        if decision.action is IngestionAction.CREATE:
            version = 1
            self._state[document_id] = DocumentState(
                document_id=document_id,
                content_hash=content_hash,
                version=version,
            )

        elif decision.action is IngestionAction.UPDATE:
            if decision.new_version is None:
                raise RuntimeError("Update decision missing new version.")

            self._state[document_id] = DocumentState(
                document_id=document_id,
                content_hash=content_hash,
                version=decision.new_version,
            )

        return decision

    def get_state(self, document_id: str) -> DocumentState | None:
        """Return current state for a document."""
        return self._state.get(document_id)

    def state_size(self) -> int:
        """Return number of tracked documents."""
        return len(self._state)
