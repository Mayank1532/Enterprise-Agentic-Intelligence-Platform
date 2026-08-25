"""Build deterministic retrieval records."""

from collections.abc import Iterable

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.retrieval import RetrievalRecord


class RetrievalRecordBuilder:
    """Convert evidence blocks into retrieval records."""

    @staticmethod
    def build(evidence: EvidenceBlock) -> RetrievalRecord:
        """Build one deterministic retrieval record."""
        return RetrievalRecord(
            evidence_id=evidence.evidence_id,
            document_id=evidence.document_id,
            chunk_id=evidence.chunk_id,
            source_path=evidence.source_path,
            chunk_index=evidence.chunk_index,
            text=evidence.text,
        )

    @classmethod
    def build_many(
        cls,
        evidence_blocks: Iterable[EvidenceBlock],
    ) -> tuple[RetrievalRecord, ...]:
        """Build retrieval records while preserving input order."""
        return tuple(cls.build(item) for item in evidence_blocks)
