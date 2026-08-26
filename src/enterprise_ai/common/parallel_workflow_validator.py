"""Validation helpers for deterministic parallel workflows."""

from enterprise_ai.core.parallel_workflow import (
    ParallelWorkflowState,
)


class ParallelWorkflowValidator:
    """Validate merged parallel workflow state."""

    def validate(
        self,
        state: ParallelWorkflowState,
    ) -> ParallelWorkflowState:
        """Validate branch completeness and evidence consistency."""
        if not state.branches:
            raise ValueError("Parallel workflow must contain branches.")

        branch_ids = [branch.branch_id for branch in state.branches]

        if len(branch_ids) != len(set(branch_ids)):
            raise ValueError("Parallel workflow contains duplicate branch IDs.")

        branch_evidence = tuple(
            evidence for branch in state.branches for evidence in branch.evidence
        )

        if branch_evidence != state.evidence:
            raise ValueError("Merged evidence does not match branch evidence.")

        return state
