"""Tests for Reciprocal Rank Fusion."""

from enterprise_ai.common.rrf import ReciprocalRankFusion
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_result import RetrievalResult


def record(
    evidence_id: str,
    chunk_id: str,
    chunk_index: int,
) -> RetrievalRecord:
    """Create a retrieval record."""
    return RetrievalRecord(
        evidence_id=evidence_id,
        document_id="document-001",
        chunk_id=chunk_id,
        source_path="hybrid.txt",
        chunk_index=chunk_index,
        text=f"text for {chunk_id}",
    )


def test_rrf_combines_results() -> None:
    """RRF combines candidates from both lists."""
    lexical = (
        RetrievalResult(record("e1", "c1", 0), 2.0),
        RetrievalResult(record("e2", "c2", 1), 1.0),
    )

    vector = (
        RetrievalResult(record("e2", "c2", 1), 0.9),
        RetrievalResult(record("e3", "c3", 2), 0.8),
    )

    results = ReciprocalRankFusion().fuse(
        lexical,
        vector,
    )

    assert len(results) == 3


def test_rrf_rewards_cross_retriever_agreement() -> None:
    """A candidate appearing in both rankings receives two contributions."""
    lexical = (RetrievalResult(record("e1", "c1", 0), 2.0),)

    vector = (RetrievalResult(record("e1", "c1", 0), 0.9),)

    results = ReciprocalRankFusion().fuse(
        lexical,
        vector,
    )

    assert len(results) == 1
    assert results[0].lexical_rank == 1
    assert results[0].vector_rank == 1
    assert results[0].fusion_score > 0


def test_rrf_is_deterministic() -> None:
    """Repeated fusion produces identical results."""
    lexical = (
        RetrievalResult(record("e1", "c1", 0), 2.0),
        RetrievalResult(record("e2", "c2", 1), 1.0),
    )

    vector = (
        RetrievalResult(record("e2", "c2", 1), 0.9),
        RetrievalResult(record("e1", "c1", 0), 0.8),
    )

    fusion = ReciprocalRankFusion()

    assert fusion.fuse(lexical, vector) == fusion.fuse(
        lexical,
        vector,
    )


def test_rrf_invalid_constant_fails_fast() -> None:
    """Invalid constants are rejected."""
    try:
        ReciprocalRankFusion(constant=0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
