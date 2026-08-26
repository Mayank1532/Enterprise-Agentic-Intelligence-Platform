"""Deterministic parallel workflow models."""

from dataclasses import dataclass

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.workflow import WorkflowState


@dataclass(frozen=True, slots=True)
class ParallelBranchResult:
    """Result produced by one isolated workflow branch."""

    branch_id: str
    evidence: tuple[EvidenceBlock, ...]
    state: WorkflowState


@dataclass(frozen=True, slots=True)
class ParallelWorkflowState:
    """Merged state produced by parallel workflow branches."""

    query: str
    branches: tuple[ParallelBranchResult, ...]
    evidence: tuple[EvidenceBlock, ...]

    @property
    def branch_count(self) -> int:
        """Return the number of completed branches."""
        return len(self.branches)

    @property
    def has_evidence(self) -> bool:
        """Return whether any branch produced evidence."""
        return bool(self.evidence)
