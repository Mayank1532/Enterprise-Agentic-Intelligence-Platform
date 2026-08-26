"""Deterministic parallel workflow implementation."""

from collections.abc import Iterable, Sequence

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.parallel_workflow import (
    ParallelBranchResult,
    ParallelWorkflowState,
)
from enterprise_ai.core.workflow import WorkflowState


class ParallelBranch:
    """Base class for an isolated parallel branch."""

    def __init__(self, branch_id: str) -> None:
        if not branch_id:
            raise ValueError("branch_id must not be empty.")

        self.branch_id = branch_id

    def execute(
        self,
        state: WorkflowState,
        evidence: Iterable[EvidenceBlock],
    ) -> ParallelBranchResult:
        """Execute the branch against isolated input."""
        branch_evidence = tuple(evidence)

        branch_state = WorkflowState(
            query=state.query,
            evidence=branch_evidence,
            output=state.output,
        )

        return ParallelBranchResult(
            branch_id=self.branch_id,
            evidence=branch_evidence,
            state=branch_state,
        )


class ParallelWorkflow:
    """Execute independent branches and merge results deterministically."""

    def __init__(
        self,
        branches: Sequence[ParallelBranch],
    ) -> None:
        if not branches:
            raise ValueError("Parallel workflow requires at least one branch.")

        branch_ids = [branch.branch_id for branch in branches]

        if len(branch_ids) != len(set(branch_ids)):
            raise ValueError("Parallel branch IDs must be unique.")

        self._branches = tuple(branches)

    @property
    def branches(self) -> tuple[ParallelBranch, ...]:
        """Return configured branches in deterministic order."""
        return self._branches

    def run(
        self,
        query: str,
        branch_evidence: Sequence[Iterable[EvidenceBlock]],
    ) -> ParallelWorkflowState:
        """Execute all branches and merge their evidence."""
        if len(branch_evidence) != len(self._branches):
            raise ValueError("Branch evidence count must match branch count.")

        initial_state = WorkflowState(query=query)

        results: list[ParallelBranchResult] = []

        for branch, evidence in zip(
            self._branches,
            branch_evidence,
            strict=True,
        ):
            result = branch.execute(
                initial_state,
                evidence,
            )
            results.append(result)

        merged_evidence = tuple(evidence for result in results for evidence in result.evidence)

        return ParallelWorkflowState(
            query=query,
            branches=tuple(results),
            evidence=merged_evidence,
        )


def merge_parallel_results(
    state: ParallelWorkflowState,
) -> tuple[EvidenceBlock, ...]:
    """Return merged evidence in deterministic branch order."""
    return tuple(evidence for branch in state.branches for evidence in branch.evidence)
