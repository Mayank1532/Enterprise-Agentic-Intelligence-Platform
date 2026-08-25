"""Tests for deterministic confidence calculation."""

import pytest

from enterprise_ai.common.confidence_calculator import ConfidenceCalculator
from enterprise_ai.core.hybrid import HybridCandidate
from enterprise_ai.core.retrieval import RetrievalRecord


def candidate(
    *,
    lexical_rank: int | None,
    vector_rank: int | None,
    fusion_score: float,
) -> HybridCandidate:
    """Create a hybrid candidate."""
    record = RetrievalRecord(
        evidence_id="evidence-001",
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=0,
        text="retrieval evidence",
    )

    return HybridCandidate(
        record=record,
        lexical_rank=lexical_rank,
        vector_rank=vector_rank,
        lexical_score=1.0,
        vector_score=1.0,
        fusion_score=fusion_score,
    )


def test_confidence_is_bounded() -> None:
    """Confidence remains within [0, 1]."""
    score = ConfidenceCalculator().calculate(
        candidate(
            lexical_rank=1,
            vector_rank=1,
            fusion_score=1.0,
        ),
        1.0,
        candidate_count=1,
    )

    assert 0.0 <= score.value <= 1.0


def test_cross_retriever_agreement_increases_confidence() -> None:
    """Agreement receives a positive confidence contribution."""
    calculator = ConfidenceCalculator()

    agreement = calculator.calculate(
        candidate(
            lexical_rank=1,
            vector_rank=1,
            fusion_score=0.05,
        ),
        0.8,
        candidate_count=2,
    )

    lexical_only = calculator.calculate(
        candidate(
            lexical_rank=1,
            vector_rank=None,
            fusion_score=0.05,
        ),
        0.8,
        candidate_count=2,
    )

    assert agreement.value > lexical_only.value


def test_invalid_candidate_count_fails() -> None:
    """Invalid candidate counts are rejected."""
    with pytest.raises(ValueError):
        ConfidenceCalculator().calculate(
            candidate(
                lexical_rank=1,
                vector_rank=1,
                fusion_score=0.05,
            ),
            0.8,
            candidate_count=0,
        )


def test_negative_rerank_score_fails() -> None:
    """Negative reranking scores are rejected."""
    with pytest.raises(ValueError):
        ConfidenceCalculator().calculate(
            candidate(
                lexical_rank=1,
                vector_rank=1,
                fusion_score=0.05,
            ),
            -0.1,
            candidate_count=2,
        )
