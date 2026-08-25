"""Deterministic evidence construction."""

import hashlib

from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.evidence import EvidenceBlock


class EvidenceBuilder:
    """Build stable evidence blocks from documents and chunks."""

    @staticmethod
    def build(
        document: DocumentRecord,
        chunk: DocumentChunk,
    ) -> EvidenceBlock:
        """Create a deterministic evidence block."""
        evidence_key = f"{document.document_id}:{chunk.chunk_id}:{chunk.text}"

        evidence_id = hashlib.sha256(evidence_key.encode()).hexdigest()

        return EvidenceBlock(
            evidence_id=evidence_id,
            document_id=document.document_id,
            chunk_id=chunk.chunk_id,
            source_path=document.source_path,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
        )
