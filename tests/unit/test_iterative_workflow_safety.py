"""Tests for iterative workflow safety guarantees."""

from enterprise_ai.common.iteration_policy import (
    SequenceEvidenceProvider,
)
from enterprise_ai.common.iterative_workflow import (
    IterativeWorkflow,
)


def test_empty_provider_is_bounded() -> None:
    """Empty evidence provider terminates at the hard limit."""
    workflow = IterativeWorkflow(
        evidence_provider=SequenceEvidenceProvider(()),
        max_iterations=7,
    )

    result = workflow.run(
        query="bounded",
    )

    assert result.iterations == 7
    assert result.output is not None
    assert result.output.status == "refused"


def test_late_evidence_terminates_on_discovery() -> None:
    """Evidence discovered later terminates the workflow."""
    from enterprise_ai.core.evidence import EvidenceBlock

    evidence = EvidenceBlock(
        evidence_id="late-001",
        document_id="document-late",
        chunk_id="chunk-late",
        source_path="document.txt",
        chunk_index=0,
        text="Late verified evidence.",
    )

    workflow = IterativeWorkflow(
        evidence_provider=SequenceEvidenceProvider(
            (
                (),
                (),
                (evidence,),
            )
        ),
        max_iterations=10,
    )

    result = workflow.run(
        query="late",
    )

    assert result.iterations == 3
    assert result.completed is True
    assert result.evidence == (evidence,)
