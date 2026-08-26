"""Deterministic sequential workflow state."""

from dataclasses import dataclass

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.structured_output import AgentOutputEnvelope


@dataclass(frozen=True, slots=True)
class WorkflowState:
    """Immutable state passed between workflow steps."""

    query: str
    evidence: tuple[EvidenceBlock, ...] = ()
    output: AgentOutputEnvelope | None = None

    @property
    def has_evidence(self) -> bool:
        """Return whether evidence is available."""
        return bool(self.evidence)
