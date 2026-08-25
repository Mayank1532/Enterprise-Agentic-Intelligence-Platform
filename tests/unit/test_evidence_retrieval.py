"""Tests for evidence-backed retrieval."""

from enterprise_ai.common.bm25_index import BM25Index
from enterprise_ai.common.deterministic_embeddings import (
    DeterministicEmbeddingProvider,
)
from enterprise_ai.common.deterministic_reranker import (
    DeterministicReranker,
)
from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.common.evidence_retrieval import (
    EvidenceRetrievalService,
)
from enterprise_ai.common.hybrid_retriever import HybridRetriever
from enterprise_ai.common.local_vector_index import LocalVectorIndex
from enterprise_ai.common.retrieval_builder import RetrievalRecordBuilder
from enterprise_ai.common.rrf import ReciprocalRankFusion
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord


def create_service() -> EvidenceRetrievalService:
    """Create the complete deterministic retrieval stack."""
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
            text="Python retrieval architecture.",
        ),
        DocumentChunk(
            chunk_id="chunk-002",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=1,
            text="Database storage architecture.",
        ),
        DocumentChunk(
            chunk_id="chunk-003",
            document_id=document.document_id,
            source_path=document.source_path,
            chunk_index=2,
            text="Python testing strategy.",
        ),
    )

    evidence = tuple(EvidenceBuilder.build(document, chunk) for chunk in chunks)

    records = RetrievalRecordBuilder.build_many(evidence)

    bm25 = BM25Index()
    bm25.add_many(records)

    vector = LocalVectorIndex(
        DeterministicEmbeddingProvider(),
    )
    vector.add_many(records)

    hybrid = HybridRetriever(
        lexical=bm25,
        vector=vector,
        fusion=ReciprocalRankFusion(),
    )

    return EvidenceRetrievalService(
        hybrid_retriever=hybrid,
        reranker=DeterministicReranker(),
    )


def test_e2e_retrieval_returns_evidence() -> None:
    """End-to-end retrieval returns evidence."""
    response = create_service().search(
        "Python retrieval",
    )

    assert response.has_evidence
    assert response.results


def test_e2e_results_have_citations() -> None:
    """Every result has complete provenance."""
    response = create_service().search(
        "Python retrieval",
    )

    for result in response.results:
        assert result.citation.evidence_id == (result.record.evidence_id)
        assert result.citation.document_id == (result.record.document_id)
        assert result.citation.chunk_id == (result.record.chunk_id)
        assert result.citation.source_path == (result.record.source_path)


def test_e2e_results_have_bounded_confidence() -> None:
    """Every result receives bounded confidence."""
    response = create_service().search(
        "Python retrieval",
    )

    assert all(0.0 <= result.confidence.value <= 1.0 for result in response.results)


def test_e2e_empty_query_returns_no_evidence() -> None:
    """Empty queries produce no evidence."""
    response = create_service().search("")

    assert response.results == ()
    assert not response.has_evidence


def test_e2e_limit_is_respected() -> None:
    """End-to-end retrieval respects the requested limit."""
    response = create_service().search(
        "Python",
        limit=1,
    )

    assert len(response.results) == 1
