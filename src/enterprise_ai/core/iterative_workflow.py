"""Deterministic bounded iterative workflow contracts."""

from dataclasses import dataclass
from enum import StrEnum

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.structured_output import AgentOutputEnvelope


class IterationDecision(StrEnum):
    """Decision returned after each workflow iteration."""

    CONTINUE = "continue"
    COMPLETE = "complete"


class IterationTermination(StrEnum):
    """Reason why an iterative workflow stopped."""

    COMPLETED = "completed"
    MAX_ITERATIONS = "max_iterations"


@dataclass(frozen=True, slots=True)
class IterationState:
    """Immutable state for one iterative workflow."""

    query: str
    iteration: int
    evidence: tuple[EvidenceBlock, ...] = ()
    output: AgentOutputEnvelope | None = None

    @property
    def has_evidence(self) -> bool:
        """Return whether evidence exists."""
        return bool(self.evidence)


@dataclass(frozen=True, slots=True)
class IterationResult:
    """Decision produced by one iteration."""

    decision: IterationDecision
    evidence: tuple[EvidenceBlock, ...] = ()


@dataclass(frozen=True, slots=True)
class IterativeWorkflowResult:
    """Final immutable result of a bounded workflow."""

    query: str
    iterations: int
    termination: IterationTermination
    evidence: tuple[EvidenceBlock, ...]
    output: AgentOutputEnvelope | None

    @property
    def completed(self) -> bool:
        """Return whether normal completion occurred."""
        return self.termination is IterationTermination.COMPLETED
