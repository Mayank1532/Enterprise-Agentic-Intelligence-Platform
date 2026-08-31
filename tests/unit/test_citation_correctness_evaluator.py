"""Tests for citation correctness evaluation."""

import pytest

from enterprise_ai.common.citation_correctness_evaluator import (
    CitationCorrectnessEvaluator,
)
from enterprise_ai.core.citation import Citation


def make_citation(evidence_id: str) -> Citation:
    return Citation(
        evidence_id=evidence_id,
        document_id="document-1",
        chunk_id=f"chunk-{evidence_id}",
        source_path="documents/source.txt",
        chunk_index=0,
    )


def test_all_citations_correct() -> None:
    evaluator = CitationCorrectnessEvaluator()

    result = evaluator.evaluate(
        citations=(
            make_citation("e1"),
            make_citation("e2"),
        ),
        valid_evidence_ids=frozenset({"e1", "e2"}),
    )

    assert result == 1.0


def test_no_citations_is_vacuously_correct() -> None:
    evaluator = CitationCorrectnessEvaluator()

    assert evaluator.evaluate(
        citations=(),
        valid_evidence_ids=frozenset({"e1"}),
    ) == 1.0


def test_partial_citation_correctness() -> None:
    evaluator = CitationCorrectnessEvaluator()

    result = evaluator.evaluate(
        citations=(
            make_citation("e1"),
            make_citation("invalid"),
        ),
        valid_evidence_ids=frozenset({"e1"}),
    )

    assert result == pytest.approx(0.5)


def test_all_citations_incorrect() -> None:
    evaluator = CitationCorrectnessEvaluator()

    result = evaluator.evaluate(
        citations=(
            make_citation("x"),
            make_citation("y"),
        ),
        valid_evidence_ids=frozenset({"e1"}),
    )

    assert result == 0.0
