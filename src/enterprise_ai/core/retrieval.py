"""Core retrieval representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalRecord:
    """Deterministic representation of evidence for retrieval."""

    evidence_id: str
    document_id: str
    chunk_id: str
    source_path: str
    chunk_index: int
    text: str
