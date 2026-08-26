"""Tests for deterministic bounded iterative workflow."""

import pytest

from enterprise_ai.common.iteration_policy import (
    IterationPolicy,
    SequenceEvidenceProvider,
)
from enterprise_ai.common.iterative_workflow import (
    IterativeWorkflow,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.iterative_workflow import (
    IterationDecision,
    IterationState,
    IterationTermination,
)


def make_evidence(
    evidence_id: str,
    text: str,
) -> EvidenceBlock:
    """Create deterministic evidence."""
    return EvidenceBlock(
        evidence_id=evidence_id,
        document_id=f"document-{evidence_id}",
        chunk_id=f"chunk-{evidence_id}",
        source_path="document.txt",
        chunk_index=0,
        text=text,
    )


def test_policy_continues_without_evidence() -> None:
    """Policy continues when evidence is unavailable."""
    state = IterationState(
        query="test",
        iteration=1,
        evidence=(),
    )

    result = IterationPolicy().evaluate(state)

    assert result.decision is IterationDecision.CONTINUE
    assert result.evidence == ()


def test_policy_completes_with_evidence() -> None:
    """Policy completes when evidence exists."""
    evidence = (
        make_evidence(
            "evidence-001",
            "Verified evidence.",
        ),
    )

    state = IterationState(
        query="test",
        iteration=2,
        evidence=evidence,
    )

    result = IterationPolicy().evaluate(state)

    assert result.decision is IterationDecision.COMPLETE
    assert result.evidence == evidence


def test_provider_returns_iteration_specific_evidence() -> None:
    """Provider returns evidence for the requested iteration."""
    evidence = make_evidence(
        "evidence-001",
        "First iteration evidence.",
    )

    provider = SequenceEvidenceProvider(
        (
            (),
            (evidence,),
        )
    )

    assert provider.get(1) == ()
    assert provider.get(2) == (evidence,)
    assert provider.get(3) == ()


def test_provider_rejects_zero_iteration() -> None:
    """Iteration numbering starts at one."""
    provider = SequenceEvidenceProvider(())

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        provider.get(0)


def test_workflow_completes_when_evidence_is_found() -> None:
    """Workflow terminates normally when evidence appears."""
    evidence = make_evidence(
        "evidence-001",
        "Verified answer.",
    )

    workflow = IterativeWorkflow(
        evidence_provider=SequenceEvidenceProvider(
            (
                (),
                (evidence,),
            )
        ),
        max_iterations=5,
    )

    result = workflow.run(
        query="Find verified answer",
    )

    assert result.iterations == 2
    assert result.termination is IterationTermination.COMPLETED
    assert result.completed is True
    assert result.evidence == (evidence,)
    assert result.output is not None
    assert result.output.status == "supported"


def test_workflow_stops_at_max_iterations() -> None:
    """Workflow cannot exceed the configured iteration limit."""
    workflow = IterativeWorkflow(
        evidence_provider=SequenceEvidenceProvider(
            (
                (),
                (),
                (),
                (),
                (),
            )
        ),
        max_iterations=3,
    )

    result = workflow.run(
        query="Never complete",
    )

    assert result.iterations == 3
    assert result.termination is IterationTermination.MAX_ITERATIONS
    assert result.completed is False
    assert result.evidence == ()
    assert result.output is not None
    assert result.output.status == "refused"


def test_workflow_rejects_zero_max_iterations() -> None:
    """Maximum iterations must be positive."""
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        IterativeWorkflow(
            evidence_provider=SequenceEvidenceProvider(()),
            max_iterations=0,
        )


def test_workflow_never_exceeds_hard_limit() -> None:
    """A non-terminating provider cannot exceed the hard limit."""
    workflow = IterativeWorkflow(
        evidence_provider=SequenceEvidenceProvider(()),
        max_iterations=2,
    )

    result = workflow.run(
        query="Hard limit",
    )

    assert result.iterations == 2
    assert result.termination is IterationTermination.MAX_ITERATIONS
