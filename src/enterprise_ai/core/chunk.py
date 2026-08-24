"""Document chunk contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    """A normalized, provenance-aware document chunk."""

    chunk_id: str
    document_id: str
    source_path: str
    chunk_index: int
    text: str
