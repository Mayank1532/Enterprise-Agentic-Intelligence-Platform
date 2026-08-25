"""Tests for deterministic retrieval metadata filtering."""

from collections.abc import Iterable

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.local_retrieval import LocalRetrievalIndex
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_filter import RetrievalFilter


def create_records() -> tuple[RetrievalRecord, ...]:
    """Create deterministic retrieval records."""
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
            text="Python retrieval architecture.",
        ),
        DocumentChunk(
            chunk_id="chunk-002",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=1,
            text="Python evidence pipeline.",
        ),
        DocumentChunk(
            chunk_id="chunk-003",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=2,
            text="Database storage layer.",
        ),
    )

    evidence = tuple(EvidenceBuilder.build(document, chunk) for chunk in chunks)

    return RetrievalRecordBuilder.build_many(evidence)


def test_filter_by_document_id() -> None:
    """Document ID filtering restricts results."""
    records = create_records()
    retrieval_filter = RetrievalFilter(document_id="document-001")

    assert all(
        retrieval_filter.matches(
            document_id=record.document_id,
            source_path=record.source_path,
            chunk_id=record.chunk_id,
            chunk_index=record.chunk_index,
        )
        for record in records
    )


def test_filter_rejects_wrong_document_id() -> None:
    """Wrong document IDs are rejected."""
    retrieval_filter = RetrievalFilter(document_id="other-document")

    assert not retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-001",
        chunk_index=0,
    )


def test_filter_by_source_path() -> None:
    """Source path filtering works."""
    retrieval_filter = RetrievalFilter(source_path="retrieval.txt")

    assert retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-001",
        chunk_index=0,
    )


def test_filter_by_chunk_id() -> None:
    """Chunk ID filtering works."""
    retrieval_filter = RetrievalFilter(chunk_id="chunk-002")

    assert retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-002",
        chunk_index=1,
    )


def test_filter_by_chunk_index() -> None:
    """Chunk index filtering works."""
    retrieval_filter = RetrievalFilter(chunk_index=1)

    assert retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-002",
        chunk_index=1,
    )


def test_filter_combines_constraints() -> None:
    """All supplied constraints must match."""
    retrieval_filter = RetrievalFilter(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-002",
        chunk_index=1,
    )

    assert retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-002",
        chunk_index=1,
    )

    assert not retrieval_filter.matches(
        document_id="document-001",
        source_path="retrieval.txt",
        chunk_id="chunk-003",
        chunk_index=2,
    )


def test_local_retrieval_applies_metadata_filter() -> None:
    """Local retrieval applies metadata constraints before ranking."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search(
        "Python",
        metadata_filter=RetrievalFilter(chunk_index=1),
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == "chunk-002"


def test_local_retrieval_without_filter_is_unchanged() -> None:
    """No filter preserves existing retrieval behavior."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python")

    assert [item.record.chunk_id for item in results] == [
        "chunk-001",
        "chunk-002",
    ]


def test_non_matching_filter_returns_empty() -> None:
    """A filter with no matching records returns no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search(
        "Python",
        metadata_filter=RetrievalFilter(
            source_path="missing.txt",
        ),
    )

    assert results == ()


def test_filter_accepts_iterable_record_source() -> None:
    """Filtering remains compatible with iterable retrieval sources."""
    records: Iterable[RetrievalRecord] = create_records()
    index = LocalRetrievalIndex()
    index.add_many(records)

    results = index.search(
        "Python",
        metadata_filter=RetrievalFilter(
            document_id="document-001",
        ),
    )

    assert len(results) == 2
