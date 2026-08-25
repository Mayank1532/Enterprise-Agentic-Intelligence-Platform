"""Tests for deterministic BM25 retrieval."""

from enterprise_ai.common.bm25_index import BM25Index
from enterprise_ai.common.evidence_builder import EvidenceBuilder
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


def test_bm25_returns_relevant_records() -> None:
    """BM25 returns relevant records."""
    index = BM25Index()
    index.add_many(create_records())

    results = index.search("Python")

    assert len(results) == 2


def test_bm25_ranks_multi_term_match_higher() -> None:
    """Documents matching more query terms rank higher."""
    index = BM25Index()
    index.add_many(create_records())

    results = index.search("Python retrieval")

    assert results[0].record.chunk_id == "chunk-001"


def test_bm25_respects_limit() -> None:
    """BM25 respects result limits."""
    index = BM25Index()
    index.add_many(create_records())

    results = index.search("Python", limit=1)

    assert len(results) == 1


def test_bm25_empty_query_returns_empty() -> None:
    """Empty queries return no results."""
    index = BM25Index()
    index.add_many(create_records())

    assert index.search("") == ()


def test_bm25_supports_metadata_filter() -> None:
    """BM25 respects retrieval metadata filters."""
    index = BM25Index()
    index.add_many(create_records())

    results = index.search(
        "Python",
        metadata_filter=RetrievalFilter(
            chunk_index=1,
        ),
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == "chunk-002"


def test_bm25_invalid_parameters_fail_fast() -> None:
    """Invalid BM25 parameters are rejected."""
    try:
        BM25Index(k1=-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    try:
        BM25Index(b=2)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
