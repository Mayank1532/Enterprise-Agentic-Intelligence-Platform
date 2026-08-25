"""Tests for the Phase 2 retrieval evaluator."""

import pytest

from enterprise_ai.common.retrieval_evaluator import (
    RetrievalEvaluator,
)
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.evidence_result import EvidenceResult, RetrievalResponse
from enterprise_ai.core.retrieval import RetrievalRecord


def make_result(evidence_id: str) -> EvidenceResult:
    """Create an evidence result."""
    record = RetrievalRecord(
        evidence_id=evidence_id,
        document_id="document-001",
        chunk_id=f"chunk-{evidence_id}",
        source_path="document.txt",
        chunk_index=0,
        text="retrieval evidence",
    )

    return EvidenceResult(
        record=record,
        confidence=ConfidenceScore(
            value=0.8,
            basis="test",
        ),
        citation=Citation(
            evidence_id=evidence_id,
            document_id="document-001",
            chunk_id=f"chunk-{evidence_id}",
            source_path="document.txt",
            chunk_index=0,
        ),
        rerank_score=0.8,
    )


def test_full_recall_passes() -> None:
    """Complete expected evidence passes evaluation."""
    response = RetrievalResponse(
        query="test",
        results=(
            make_result("e1"),
            make_result("e2"),
        ),
    )

    report = RetrievalEvaluator().evaluate(
        response,
        ("e1", "e2"),
    )

    assert report.passed
    assert report.metrics[0].value == 1.0


def test_partial_recall_fails() -> None:
    """Missing expected evidence fails evaluation."""
    response = RetrievalResponse(
        query="test",
        results=(make_result("e1"),),
    )

    report = RetrievalEvaluator().evaluate(
        response,
        ("e1", "e2"),
        minimum_recall=1.0,
    )

    assert not report.passed
    assert report.metrics[0].value == 0.5


def test_empty_expectation_is_valid() -> None:
    """No expected evidence is valid only when nothing is retrieved."""
    response = RetrievalResponse(
        query="test",
        results=(),
    )

    report = RetrievalEvaluator().evaluate(
        response,
        (),
    )

    assert report.passed
    assert report.metrics[0].value == 1.0


def test_invalid_threshold_fails() -> None:
    """Invalid evaluation thresholds are rejected."""
    response = RetrievalResponse(
        query="test",
        results=(),
    )

    with pytest.raises(ValueError):
        RetrievalEvaluator().evaluate(
            response,
            (),
            minimum_recall=1.5,
        )
