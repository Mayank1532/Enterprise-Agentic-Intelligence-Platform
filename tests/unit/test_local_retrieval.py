"""Tests for deterministic local retrieval."""

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.local_retrieval import LocalRetrievalIndex
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.retrieval import RetrievalRecord


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


def test_search_returns_relevant_records() -> None:
    """Search returns records containing query tokens."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python")

    assert len(results) == 2
    assert [item.record.chunk_id for item in results] == [
        "chunk-001",
        "chunk-002",
    ]


def test_search_ranks_by_score_then_chunk_index() -> None:
    """Search uses deterministic ranking."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python retrieval")

    assert [item.record.chunk_id for item in results] == [
        "chunk-001",
        "chunk-002",
    ]
    assert results[0].score == 2
    assert results[1].score == 1


def test_search_respects_limit() -> None:
    """Search respects the requested result limit."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python", limit=1)

    assert len(results) == 1
    assert results[0].record.chunk_id == "chunk-001"


def test_search_empty_query_returns_empty() -> None:
    """Empty queries return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("") == ()


def test_search_non_matching_query_returns_empty() -> None:
    """Non-matching queries return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("quantum") == ()


def test_search_non_positive_limit_returns_empty() -> None:
    """Non-positive limits return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("Python", limit=0) == ()
    assert index.search("Python", limit=-1) == ()
