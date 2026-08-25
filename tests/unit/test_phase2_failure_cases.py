"""Final Phase 2 retrieval failure and edge-case tests."""

import pytest

from enterprise_ai.common.bm25_index import BM25Index
from enterprise_ai.common.deterministic_embeddings import (
    DeterministicEmbeddingProvider,
)
from enterprise_ai.common.deterministic_reranker import (
    DeterministicReranker,
)
from enterprise_ai.common.local_vector_index import LocalVectorIndex
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.evidence_result import (
    EvidenceResult,
    RetrievalResponse,
)
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_result import RetrievalResult


def record() -> RetrievalRecord:
    """Create a deterministic retrieval record."""
    return RetrievalRecord(
        evidence_id="evidence-001",
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=0,
        text="Python retrieval evidence",
    )


def test_bm25_empty_index_is_safe() -> None:
    """Empty BM25 indexes return no results."""
    assert BM25Index().search("Python") == ()


def test_vector_empty_index_is_safe() -> None:
    """Empty vector indexes return no results."""
    index = LocalVectorIndex(
        DeterministicEmbeddingProvider(),
    )

    assert index.search("Python") == ()


def test_negative_limits_are_safe() -> None:
    """Negative limits return no results."""
    record_value = record()

    lexical = BM25Index()
    lexical.add_many(
        (
            RetrievalRecord(
                evidence_id=record_value.evidence_id,
                document_id=record_value.document_id,
                chunk_id=record_value.chunk_id,
                source_path=record_value.source_path,
                chunk_index=record_value.chunk_index,
                text=record_value.text,
            ),
        )
    )

    assert (
        lexical.search(
            "Python",
            limit=-1,
        )
        == ()
    )


def test_invalid_confidence_is_rejected() -> None:
    """Confidence outside bounds is rejected."""
    with pytest.raises(ValueError):
        ConfidenceScore(
            value=1.1,
            basis="test",
        )

    with pytest.raises(ValueError):
        ConfidenceScore(
            value=-0.1,
            basis="test",
        )


def test_invalid_citation_is_rejected() -> None:
    """Invalid provenance is rejected."""
    with pytest.raises(ValueError):
        Citation(
            evidence_id="",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=0,
        )


def test_negative_rerank_score_is_rejected() -> None:
    """Negative reranking scores are rejected."""
    with pytest.raises(ValueError):
        EvidenceResult(
            record=record(),
            confidence=ConfidenceScore(
                value=0.5,
                basis="test",
            ),
            citation=Citation(
                evidence_id="evidence-001",
                document_id="document-001",
                chunk_id="chunk-001",
                source_path="document.txt",
                chunk_index=0,
            ),
            rerank_score=-0.1,
        )


def test_empty_response_reports_no_evidence() -> None:
    """Empty retrieval responses remain explicit."""
    response = RetrievalResponse(
        query="unknown",
        results=(),
    )

    assert not response.has_evidence


def test_retrieval_result_score_accepts_fractional_values() -> None:
    """Retrieval scores support real-valued ranking."""
    result = RetrievalResult(
        record=record(),
        score=0.7345,
    )

    assert result.score == 0.7345


def test_reranker_rejects_no_candidates_only_by_output_contract() -> None:
    """Empty candidate input produces an empty score tuple."""
    assert (
        DeterministicReranker().rerank(
            "Python",
            (),
        )
        == ()
    )
