"""Deterministic retrieval metadata filtering."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalFilter:
    """Optional metadata constraints for retrieval."""

    document_id: str | None = None
    source_path: str | None = None
    chunk_id: str | None = None
    chunk_index: int | None = None

    def matches(
        self,
        *,
        document_id: str,
        source_path: str,
        chunk_id: str,
        chunk_index: int,
    ) -> bool:
        """Return whether supplied metadata satisfies all constraints."""
        if self.document_id is not None and document_id != self.document_id:
            return False

        if self.source_path is not None and source_path != self.source_path:
            return False

        if self.chunk_id is not None and chunk_id != self.chunk_id:
            return False

        if self.chunk_index is not None and chunk_index != self.chunk_index:
            return False

        return True
