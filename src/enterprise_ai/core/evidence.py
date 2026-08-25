"""Deterministic evidence representation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceBlock:
    """A stable, citation-ready unit of source evidence."""

    evidence_id: str
    document_id: str
    chunk_id: str
    source_path: str
    chunk_index: int
    text: str

    def reference(self) -> str:
        """Return a stable human-readable evidence reference."""
        return (
            f"{self.document_id}#"
            f"{self.chunk_id}"
        )
