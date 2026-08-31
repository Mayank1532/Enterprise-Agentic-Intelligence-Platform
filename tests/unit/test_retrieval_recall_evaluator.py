"""Tests for Phase 8 retrieval recall evaluation."""

import pytest

from enterprise_ai.common.retrieval_recall_evaluator import (
    RetrievalRecallEvaluator,
)
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.evidence_result import (
    EvidenceResult,
    RetrievalResponse,
)
from enterprise_ai.core.retrieval import RetrievalRecord


def make_evidence(evidence_id: str) -> EvidenceResult:
    """Create deterministic evidence using the real project contracts."""
    record = RetrievalRecord(
        evidence_id=evidence_id,
        document_id=f"document-{evidence_id}",
        chunk_id=f"chunk-{evidence_id}",
        source_path=f"/test/{evidence_id}.txt",
        chunk_index=0,
        text=f"content for {evidence_id}",
    )

    citation = Citation(
        evidence_id=record.evidence_id,
        document_id=record.document_id,
        chunk_id=record.chunk_id,
        source_path=record.source_path,
        chunk_index=record.chunk_index,
    )

    return EvidenceResult(
        record=record,
        confidence=ConfidenceScore(
            value=1.0,
            basis="deterministic test fixture",
        ),
        citation=citation,
        rerank_score=1.0,
    )


def make_response(*evidence_ids: str) -> RetrievalResponse:
    """Create a deterministic retrieval response."""
    return RetrievalResponse(
        query="test query",
        results=tuple(
            make_evidence(evidence_id)
            for evidence_id in evidence_ids
        ),
    )


def test_full_recall_passes() -> None:
    """All expected evidence is retrieved."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1", "e2"),
        ("e1", "e2"),
    )

    assert report.passed
    assert len(report.metrics) == 1
    assert report.metrics[0].name == "retrieval_recall"
    assert report.metrics[0].value == 1.0
    assert report.metrics[0].passed


def test_partial_recall_is_calculated_correctly() -> None:
    """Only half of expected evidence is retrieved."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1"),
        ("e1", "e2"),
    )

    assert report.metrics[0].value == pytest.approx(0.5)
    assert not report.metrics[0].passed
    assert not report.passed


def test_zero_recall_is_calculated_correctly() -> None:
    """No expected evidence is retrieved."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("irrelevant"),
        ("e1", "e2"),
    )

    assert report.metrics[0].value == 0.0
    assert not report.metrics[0].passed
    assert not report.passed


def test_empty_expectation_with_empty_retrieval_passes() -> None:
    """No expected evidence and no retrieved evidence is a perfect recall case."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response(),
        (),
    )

    assert report.metrics[0].value == 1.0
    assert report.metrics[0].passed
    assert report.passed


def test_empty_retrieval_with_expected_evidence_has_zero_recall() -> None:
    """Expected evidence with no retrieval produces zero recall."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response(),
        ("e1",),
    )

    assert report.metrics[0].value == 0.0
    assert not report.metrics[0].passed
    assert not report.passed


def test_one_of_three_expected_evidence_items_gives_one_third_recall() -> None:
    """One retrieved item out of three expected items gives one-third recall."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1"),
        ("e1", "e2", "e3"),
    )

    assert report.metrics[0].value == pytest.approx(1 / 3)
    assert not report.metrics[0].passed


def test_custom_recall_threshold_is_respected() -> None:
    """A partial recall can pass when the configured threshold permits it."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1"),
        ("e1", "e2"),
        minimum_recall=0.5,
    )

    assert report.metrics[0].value == pytest.approx(0.5)
    assert report.metrics[0].passed
    assert report.passed


@pytest.mark.parametrize(
    "minimum_recall",
    [-0.1, 1.1],
)
def test_invalid_recall_threshold_is_rejected(
    minimum_recall: float,
) -> None:
    """Recall thresholds outside the normalized range are rejected."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        RetrievalRecallEvaluator().evaluate(
            make_response("e1"),
            ("e1",),
            minimum_recall=minimum_recall,
        )


def test_blank_expected_ids_are_ignored() -> None:
    """Blank expected evidence identifiers do not affect recall."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1"),
        ("e1", "", "   "),
    )

    assert report.metrics[0].value == 1.0
    assert report.passed


def test_duplicate_retrieved_evidence_does_not_inflate_recall() -> None:
    """Repeated retrieved evidence identifiers count only once."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1", "e1"),
        ("e1", "e2"),
    )

    assert report.metrics[0].value == pytest.approx(0.5)


def test_extra_retrieved_evidence_does_not_inflate_recall() -> None:
    """Unexpected evidence does not increase expected-evidence recall."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1", "e2", "unexpected"),
        ("e1", "e2"),
    )

    assert report.metrics[0].value == 1.0
    assert report.passed


def test_recall_report_uses_canonical_evaluation_report() -> None:
    """Recall evaluation returns the canonical evaluation report."""
    report = RetrievalRecallEvaluator().evaluate(
        make_response("e1"),
        ("e1",),
    )

    assert type(report).__name__ == "EvaluationReport"
    assert report.metrics[0].name == "retrieval_recall"


def test_recall_uses_evidence_record_identifier() -> None:
    """Recall is based on the RetrievalRecord evidence identifier."""
    response = make_response("evidence-001")

    report = RetrievalRecallEvaluator().evaluate(
        response,
        ("evidence-001",),
    )

    assert report.metrics[0].value == 1.0
    assert report.passed
