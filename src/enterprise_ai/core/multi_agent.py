"""Deterministic multi-agent orchestration contracts."""

from dataclasses import dataclass
from enum import StrEnum

from enterprise_ai.core.evidence import EvidenceBlock


class AgentType(StrEnum):
    """Canonical agent identities."""

    DOCUMENT = "document"
    WEB = "web"
    DATA = "data"


class AgentStatus(StrEnum):
    """Execution status for one agent."""

    SUCCESS = "success"
    FAILED = "failed"


class SupervisorStatus(StrEnum):
    """Overall multi-agent execution status."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class AgentTask:
    """Task delegated to one agent."""

    task_id: str
    agent_type: AgentType
    query: str


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Result returned by one agent."""

    task_id: str
    agent_type: AgentType
    status: AgentStatus
    evidence: tuple[EvidenceBlock, ...] = ()
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SupervisorResult:
    """Aggregated result returned by the supervisor."""

    query: str
    status: SupervisorStatus
    agent_results: tuple[AgentResult, ...]
    evidence: tuple[EvidenceBlock, ...]

    @property
    def successful_agents(self) -> int:
        """Return number of successful agents."""
        return sum(result.status is AgentStatus.SUCCESS for result in self.agent_results)

    @property
    def failed_agents(self) -> int:
        """Return number of failed agents."""
        return sum(result.status is AgentStatus.FAILED for result in self.agent_results)
