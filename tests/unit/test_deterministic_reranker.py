"""Tests for the deterministic reranker."""

from enterprise_ai.common.deterministic_reranker import (
    DeterministicReranker,
)
from enterprise_ai.core.retrieval import RetrievalRecord


def records() -> tuple[RetrievalRecord, ...]:
    """Create reranking candidates."""
    return (
        RetrievalRecord(
            evidence_id="e1",
            document_id="d1",
            chunk_id="c1",
            source_path="a.txt",
            chunk_index=0,
            text="Python retrieval architecture",
        ),
        RetrievalRecord(
            evidence_id="e2",
            document_id="d1",
            chunk_id="c2",
            source_path="a.txt",
            chunk_index=1,
            text="Database storage",
        ),
    )


def test_reranker_scores_query_coverage() -> None:
    """Matching candidates receive higher scores."""
    scores = DeterministicReranker().rerank(
        "Python retrieval",
        records(),
    )

    assert scores[0] == 1.0
    assert scores[1] == 0.0


def test_reranker_is_deterministic() -> None:
    """Repeated reranking is identical."""
    reranker = DeterministicReranker()

    assert reranker.rerank(
        "Python",
        records(),
    ) == reranker.rerank(
        "Python",
        records(),
    )


def test_empty_query_returns_zero_scores() -> None:
    """Empty queries return zero scores."""
    scores = DeterministicReranker().rerank(
        "",
        records(),
    )

    assert scores == (0.0, 0.0)
