"""Tests for deterministic parallel workflow."""

import pytest

from enterprise_ai.common.parallel_workflow import (
    ParallelBranch,
    ParallelWorkflow,
    merge_parallel_results,
)
from enterprise_ai.common.parallel_workflow_validator import (
    ParallelWorkflowValidator,
)
from enterprise_ai.core.evidence import EvidenceBlock


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


def test_parallel_branch_requires_id() -> None:
    """Branch IDs must be non-empty."""
    with pytest.raises(
        ValueError,
        match="branch_id",
    ):
        ParallelBranch("")


def test_parallel_workflow_requires_branches() -> None:
    """Parallel workflow cannot be empty."""
    with pytest.raises(
        ValueError,
        match="at least one branch",
    ):
        ParallelWorkflow(())


def test_parallel_workflow_requires_unique_branch_ids() -> None:
    """Branch IDs must be unique."""
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        ParallelWorkflow(
            (
                ParallelBranch("research"),
                ParallelBranch("research"),
            )
        )


def test_parallel_workflow_executes_all_branches() -> None:
    """All configured branches produce results."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("documents"),
            ParallelBranch("metadata"),
            ParallelBranch("lexical"),
        )
    )

    result = workflow.run(
        query="test",
        branch_evidence=(
            (
                make_evidence(
                    "evidence-001",
                    "document evidence",
                ),
            ),
            (
                make_evidence(
                    "evidence-002",
                    "metadata evidence",
                ),
            ),
            (
                make_evidence(
                    "evidence-003",
                    "lexical evidence",
                ),
            ),
        ),
    )

    assert result.branch_count == 3
    assert [branch.branch_id for branch in result.branches] == [
        "documents",
        "metadata",
        "lexical",
    ]


def test_parallel_merge_preserves_branch_order() -> None:
    """Merged evidence follows deterministic branch order."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("first"),
            ParallelBranch("second"),
        )
    )

    result = workflow.run(
        query="order",
        branch_evidence=(
            (
                make_evidence(
                    "evidence-001",
                    "first",
                ),
                make_evidence(
                    "evidence-002",
                    "first-second",
                ),
            ),
            (
                make_evidence(
                    "evidence-003",
                    "second",
                ),
            ),
        ),
    )

    assert [item.evidence_id for item in result.evidence] == [
        "evidence-001",
        "evidence-002",
        "evidence-003",
    ]


def test_parallel_merge_helper_matches_state() -> None:
    """Merge helper returns the same deterministic evidence."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("a"),
            ParallelBranch("b"),
        )
    )

    result = workflow.run(
        query="merge",
        branch_evidence=(
            (make_evidence("evidence-001", "A"),),
            (make_evidence("evidence-002", "B"),),
        ),
    )

    assert merge_parallel_results(result) == result.evidence


def test_parallel_workflow_rejects_wrong_branch_count() -> None:
    """Evidence input count must match configured branches."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("a"),
            ParallelBranch("b"),
        )
    )

    with pytest.raises(
        ValueError,
        match="count",
    ):
        workflow.run(
            query="mismatch",
            branch_evidence=((make_evidence("evidence-001", "A"),),),
        )


def test_parallel_workflow_can_have_empty_branch() -> None:
    """A branch may legitimately produce no evidence."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("documents"),
            ParallelBranch("metadata"),
        )
    )

    result = workflow.run(
        query="partial",
        branch_evidence=(
            (
                make_evidence(
                    "evidence-001",
                    "document",
                ),
            ),
            (),
        ),
    )

    assert result.branch_count == 2
    assert result.has_evidence is True
    assert len(result.evidence) == 1


def test_validator_accepts_valid_parallel_state() -> None:
    """Validator accepts internally consistent state."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("a"),
            ParallelBranch("b"),
        )
    )

    state = workflow.run(
        query="validate",
        branch_evidence=(
            (make_evidence("evidence-001", "A"),),
            (make_evidence("evidence-002", "B"),),
        ),
    )

    validated = ParallelWorkflowValidator().validate(state)

    assert validated == state


def test_validator_rejects_inconsistent_merged_evidence() -> None:
    """Validator rejects manually corrupted merged evidence."""
    workflow = ParallelWorkflow(
        (
            ParallelBranch("a"),
            ParallelBranch("b"),
        )
    )

    state = workflow.run(
        query="invalid",
        branch_evidence=(
            (make_evidence("evidence-001", "A"),),
            (make_evidence("evidence-002", "B"),),
        ),
    )

    from dataclasses import replace

    corrupted = replace(
        state,
        evidence=(),
    )

    with pytest.raises(
        ValueError,
        match="Merged evidence",
    ):
        ParallelWorkflowValidator().validate(corrupted)
