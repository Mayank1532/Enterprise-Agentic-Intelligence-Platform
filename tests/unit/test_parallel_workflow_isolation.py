"""Tests for parallel branch isolation."""

from collections.abc import Iterable

from enterprise_ai.common.parallel_workflow import (
    ParallelBranch,
    ParallelWorkflow,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.parallel_workflow import ParallelBranchResult
from enterprise_ai.core.workflow import WorkflowState


class TrackingBranch(ParallelBranch):
    """Branch that records the state it receives."""

    def __init__(
        self,
        branch_id: str,
        observed: list[tuple[str, tuple[EvidenceBlock, ...]]],
    ) -> None:
        super().__init__(branch_id)
        self._observed = observed

    def execute(
        self,
        state: WorkflowState,
        evidence: Iterable[EvidenceBlock],
    ) -> ParallelBranchResult:
        evidence_tuple = tuple(evidence)

        self._observed.append(
            (
                self.branch_id,
                state.evidence,
            )
        )

        return super().execute(
            state,
            evidence_tuple,
        )


def test_branches_receive_same_clean_initial_state() -> None:
    """Each branch starts from the same isolated workflow state."""
    observed: list[tuple[str, tuple[EvidenceBlock, ...]]] = []

    workflow = ParallelWorkflow(
        (
            TrackingBranch("first", observed),
            TrackingBranch("second", observed),
            TrackingBranch("third", observed),
        )
    )

    workflow.run(
        query="isolation",
        branch_evidence=(
            (),
            (),
            (),
        ),
    )

    assert observed == [
        ("first", ()),
        ("second", ()),
        ("third", ()),
    ]
