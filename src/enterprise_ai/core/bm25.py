"""BM25 retrieval representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BM25Document:
    """Tokenized document representation for BM25 scoring."""

    document_id: str
    chunk_id: str
    evidence_id: str
    source_path: str
    chunk_index: int
    text: str
    tokens: tuple[str, ...]
