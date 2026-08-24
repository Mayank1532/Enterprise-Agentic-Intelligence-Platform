"""Document provenance contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentRecord:
    """Canonical metadata for an ingested document."""

    document_id: str
    source_path: str
    content_hash: str
    size_bytes: int
    suffix: str
    reused: bool
