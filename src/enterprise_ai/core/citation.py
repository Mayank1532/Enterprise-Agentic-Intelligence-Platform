"""Deterministic citation representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Citation:
    """Provenance citation for retrieved evidence."""

    evidence_id: str
    document_id: str
    chunk_id: str
    source_path: str
    chunk_index: int

    def __post_init__(self) -> None:
        """Validate citation identity."""
        fields = (
            self.evidence_id,
            self.document_id,
            self.chunk_id,
            self.source_path,
        )

        if any(not field.strip() for field in fields):
            raise ValueError("citation identity fields must not be empty")

        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")
