"""Tests for deterministic local vector retrieval."""

from enterprise_ai.common.deterministic_embeddings import (
    DeterministicEmbeddingProvider,
)
from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.local_vector_index import LocalVectorIndex
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_filter import RetrievalFilter


def create_records() -> tuple[RetrievalRecord, ...]:
    """Create deterministic retrieval records."""
    document = DocumentRecord(
        document_id="document-001",
        source_path="vector.txt",
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
            text="Database storage layer.",
        ),
    )

    evidence = tuple(EvidenceBuilder.build(document, chunk) for chunk in chunks)

    return RetrievalRecordBuilder.build_many(evidence)


def test_vector_index_returns_results() -> None:
    """Vector index returns matching results."""
    provider = DeterministicEmbeddingProvider()
    index = LocalVectorIndex(provider)

    index.add_many(create_records())

    results = index.search("Python retrieval")

    assert results


def test_vector_index_is_deterministic() -> None:
    """Repeated vector searches return the same ordering."""
    provider = DeterministicEmbeddingProvider()
    index = LocalVectorIndex(provider)

    index.add_many(create_records())

    first = index.search("Python retrieval")
    second = index.search("Python retrieval")

    assert first == second


def test_vector_index_respects_limit() -> None:
    """Vector search respects the result limit."""
    provider = DeterministicEmbeddingProvider()
    index = LocalVectorIndex(provider)

    index.add_many(create_records())

    assert len(index.search("Python", limit=1)) == 1


def test_vector_index_supports_metadata_filter() -> None:
    """Vector search respects metadata filters."""
    provider = DeterministicEmbeddingProvider()
    index = LocalVectorIndex(provider)

    index.add_many(create_records())

    results = index.search(
        "Python",
        metadata_filter=RetrievalFilter(
            chunk_index=0,
        ),
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == "chunk-001"


def test_vector_index_empty_query_returns_empty() -> None:
    """Empty queries return no vector results."""
    provider = DeterministicEmbeddingProvider()
    index = LocalVectorIndex(provider)

    index.add_many(create_records())

    assert index.search("") == ()
