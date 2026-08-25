"""Tests for deterministic local retrieval."""

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.common.local_retrieval import LocalRetrievalIndex
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord


def create_records():
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

    evidence = tuple(
        EvidenceBuilder.build(document, chunk)
        for chunk in chunks
    )

    return RetrievalRecordBuilder.build_many(evidence)


def test_search_returns_matching_records() -> None:
    """Search returns records containing query terms."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python")

    assert len(results) == 2
    assert {item.record.chunk_id for item in results} == {
        "chunk-001",
        "chunk-002",
    }


def test_search_is_case_insensitive() -> None:
    """Search normalizes query and document casing."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("PYTHON")

    assert len(results) == 2


def test_search_ranks_by_token_overlap() -> None:
    """Records with more matching terms rank first."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python retrieval")

    assert results[0].record.chunk_id == "chunk-001"
    assert results[0].score == 2
    assert results[1].record.chunk_id == "chunk-002"
    assert results[1].score == 1


def test_search_preserves_deterministic_tie_order() -> None:
    """Equal scores are ordered by chunk index."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python")

    assert [item.record.chunk_index for item in results] == [0, 1]


def test_search_respects_limit() -> None:
    """Search returns no more than the requested limit."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    results = index.search("Python", limit=1)

    assert len(results) == 1


def test_search_empty_query() -> None:
    """Empty queries return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("   ") == ()


def test_search_no_match() -> None:
    """Unknown terms return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("quantum") == ()


def test_search_non_positive_limit() -> None:
    """Non-positive limits return no results."""
    index = LocalRetrievalIndex()
    index.add_many(create_records())

    assert index.search("Python", limit=0) == ()
    assert index.search("Python", limit=-1) == ()


def test_empty_index() -> None:
    """An empty index returns no results."""
    index = LocalRetrievalIndex()

    assert index.search("Python") == ()
