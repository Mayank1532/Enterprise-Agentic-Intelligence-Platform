"""Tests for deterministic evidence collection."""

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.evidence_collector import EvidenceCollector
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord


def create_inputs() -> tuple[DocumentRecord, tuple[DocumentChunk, ...]]:
    """Create deterministic collection inputs."""
    document = DocumentRecord(
        document_id="document-001",
        source_path="evidence.txt",
        content_hash="content-hash-001",
        size_bytes=100,
        suffix=".txt",
        reused=False,
    )

    chunks = (
        DocumentChunk(
            chunk_id="chunk-001",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=0,
            text="First evidence.",
        ),
        DocumentChunk(
            chunk_id="chunk-002",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=1,
            text="Second evidence.",
        ),
    )

    return document, chunks


def test_collect_returns_all_evidence() -> None:
    """Collector returns one evidence block per chunk."""
    document, chunks = create_inputs()

    evidence = EvidenceCollector().collect(document, chunks)

    assert len(evidence) == 2
    assert evidence[0].chunk_id == "chunk-001"
    assert evidence[1].chunk_id == "chunk-002"


def test_collect_preserves_chunk_order() -> None:
    """Evidence follows deterministic chunk order."""
    document, chunks = create_inputs()

    evidence = EvidenceCollector().collect(document, chunks)

    assert [item.chunk_index for item in evidence] == [0, 1]


def test_collect_matches_direct_builder() -> None:
    """Collection produces the same blocks as direct construction."""
    document, chunks = create_inputs()

    collected = EvidenceCollector().collect(document, chunks)
    expected = tuple(EvidenceBuilder.build(document, chunk) for chunk in chunks)

    assert collected == expected


def test_collect_empty_chunks() -> None:
    """Empty input produces an empty evidence collection."""
    document, _ = create_inputs()

    evidence = EvidenceCollector().collect(document, ())

    assert evidence == ()
