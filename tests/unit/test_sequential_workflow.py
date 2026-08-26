"""Tests for deterministic sequential workflow."""

import pytest

from enterprise_ai.common.sequential_workflow import (
    EvidenceStep,
    SequentialWorkflow,
    StructuredOutputStep,
    WorkflowValidationStep,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.workflow import WorkflowState


def make_evidence(
    evidence_id: str = "evidence-001",
    text: str = "Verified evidence.",
) -> EvidenceBlock:
    """Create deterministic evidence."""
    return EvidenceBlock(
        evidence_id=evidence_id,
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=0,
        text=text,
    )


def test_evidence_step_preserves_order() -> None:
    """Evidence step preserves deterministic input order."""
    state = WorkflowState(query="test")

    evidence = (
        make_evidence("evidence-001"),
        make_evidence("evidence-002"),
    )

    result = EvidenceStep().execute(
        state,
        evidence,
    )

    assert [item.evidence_id for item in result.evidence] == [
        "evidence-001",
        "evidence-002",
    ]


def test_output_step_creates_supported_result() -> None:
    """Evidence produces a supported structured result."""
    state = WorkflowState(
        query="test",
        evidence=(make_evidence(),),
    )

    result = StructuredOutputStep().execute(state)

    assert result.output is not None
    assert result.output.status == "supported"
    assert result.output.result.supported is True
    assert result.output.result.evidence


def test_output_step_refuses_without_evidence() -> None:
    """Missing evidence produces an explicit refusal."""
    state = WorkflowState(query="test")

    result = StructuredOutputStep().execute(state)

    assert result.output is not None
    assert result.output.status == "refused"
    assert result.output.result.supported is False
    assert result.output.result.refusal_reason == "insufficient evidence"


def test_validation_requires_output() -> None:
    """Validation rejects incomplete workflow state."""
    state = WorkflowState(query="test")

    with pytest.raises(
        ValueError,
        match="without structured output",
    ):
        WorkflowValidationStep().execute(state)


def test_validation_accepts_supported_output() -> None:
    """Validation accepts evidence-backed supported output."""
    state = WorkflowState(
        query="test",
        evidence=(make_evidence(),),
    )

    state = StructuredOutputStep().execute(state)

    result = WorkflowValidationStep().execute(state)

    assert result == state


def test_complete_workflow_is_sequential() -> None:
    """Complete workflow executes all deterministic stages."""
    workflow = SequentialWorkflow()

    result = workflow.run(
        query="What is verified?",
        evidence=(make_evidence(),),
    )

    assert result.query == "What is verified?"
    assert len(result.evidence) == 1
    assert result.output is not None
    assert result.output.status == "supported"


def test_complete_workflow_refuses_without_evidence() -> None:
    """Complete workflow refuses when no evidence exists."""
    workflow = SequentialWorkflow()

    result = workflow.run(
        query="Unknown question",
        evidence=(),
    )

    assert result.output is not None
    assert result.output.status == "refused"
    assert result.output.result.is_refusal()


def test_workflow_preserves_multiple_evidence_blocks() -> None:
    """All evidence blocks reach the final structured result."""
    workflow = SequentialWorkflow()

    evidence = (
        make_evidence("evidence-001", "First."),
        make_evidence("evidence-002", "Second."),
        make_evidence("evidence-003", "Third."),
    )

    result = workflow.run(
        query="Multiple evidence",
        evidence=evidence,
    )

    assert result.output is not None
    assert len(result.output.result.evidence) == 3
    assert [item.evidence_id for item in result.output.result.evidence] == [
        "evidence-001",
        "evidence-002",
        "evidence-003",
    ]
