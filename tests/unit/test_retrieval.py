"""Tests for deterministic retrieval representation."""

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.evidence import EvidenceBlock


def create_evidence() -> tuple[EvidenceBlock, ...]:
    """Create deterministic evidence input."""
    document = DocumentRecord(
        document_id="document-001",
        source_path="retrieval.txt",
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
            text="First retrieval record.",
        ),
        DocumentChunk(
            chunk_id="chunk-002",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=1,
            text="Second retrieval record.",
        ),
    )

    return tuple(EvidenceBuilder.build(document, chunk) for chunk in chunks)


def test_build_preserves_evidence_identity() -> None:
    """Retrieval records preserve evidence identity."""
    evidence = create_evidence()[0]

    record = RetrievalRecordBuilder.build(evidence)

    assert record.evidence_id == evidence.evidence_id
    assert record.document_id == evidence.document_id
    assert record.chunk_id == evidence.chunk_id


def test_build_preserves_source_metadata() -> None:
    """Retrieval records preserve provenance metadata."""
    evidence = create_evidence()[0]

    record = RetrievalRecordBuilder.build(evidence)

    assert record.source_path == evidence.source_path
    assert record.chunk_index == evidence.chunk_index


def test_build_preserves_text() -> None:
    """Retrieval records contain the original evidence text."""
    evidence = create_evidence()[0]

    record = RetrievalRecordBuilder.build(evidence)

    assert record.text == evidence.text


def test_build_many_preserves_order() -> None:
    """Bulk construction preserves deterministic order."""
    evidence = create_evidence()

    records = RetrievalRecordBuilder.build_many(evidence)

    assert len(records) == 2
    assert [record.chunk_index for record in records] == [0, 1]
    assert [record.chunk_id for record in records] == [
        "chunk-001",
        "chunk-002",
    ]


def test_build_many_empty_input() -> None:
    """Empty evidence produces empty retrieval representation."""
    assert RetrievalRecordBuilder.build_many(()) == ()
