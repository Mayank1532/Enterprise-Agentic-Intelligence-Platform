"""Deterministic evidence collection."""

from collections.abc import Iterable

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.evidence import EvidenceBlock


class EvidenceCollector:
    """Collect deterministic evidence blocks from document chunks."""

    def collect(
        self,
        document: DocumentRecord,
        chunks: Iterable[DocumentChunk],
    ) -> tuple[EvidenceBlock, ...]:
        """Build evidence blocks while preserving chunk order."""
        evidence = tuple(
            EvidenceBuilder.build(document, chunk)
            for chunk in chunks
        )

        return evidence
