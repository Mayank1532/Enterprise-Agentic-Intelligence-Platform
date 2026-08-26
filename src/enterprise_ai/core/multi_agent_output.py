"""Evidence-backed output for multi-agent orchestration."""

from dataclasses import dataclass

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import SupervisorResult
from enterprise_ai.core.structured_output import AgentOutputEnvelope


@dataclass(frozen=True, slots=True)
class MultiAgentOutput:
    """Final evidence-backed multi-agent response."""

    result: SupervisorResult
    output: AgentOutputEnvelope
    evidence: tuple[EvidenceBlock, ...]
