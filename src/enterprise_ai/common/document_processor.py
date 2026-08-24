"""Deterministic document extraction and chunking."""

import hashlib
from pathlib import Path

from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord


class TextDocumentProcessor:
    """Extract UTF-8 text and create bounded document chunks."""

    def __init__(self, chunk_size: int = 1000) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        self.chunk_size = chunk_size

    def extract(self, path: Path) -> str:
        """Read a UTF-8 text document incrementally."""
        parts: list[str] = []

        with path.open("r", encoding="utf-8") as file:
            while chunk := file.read(self.chunk_size):
                parts.append(chunk)

        return "".join(parts)

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize whitespace deterministically."""
        return " ".join(text.split())

    def chunk(
        self,
        document: DocumentRecord,
        text: str,
    ) -> list[DocumentChunk]:
        """Create deterministic chunks while preserving provenance."""
        normalized = self.normalize(text)

        if not normalized:
            return []

        chunks: list[DocumentChunk] = []

        for index, start in enumerate(
            range(0, len(normalized), self.chunk_size)
        ):
            chunk_text = normalized[start : start + self.chunk_size]

            chunk_id = hashlib.sha256(
                f"{document.document_id}:{index}:{chunk_text}".encode()
            ).hexdigest()

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    source_path=document.source_path,
                    chunk_index=index,
                    text=chunk_text,
                )
            )

        return chunks

