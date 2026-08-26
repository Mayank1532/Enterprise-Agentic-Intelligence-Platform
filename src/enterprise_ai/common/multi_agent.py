"""Deterministic multi-agent execution layer."""

from collections.abc import Iterable

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import (
    AgentResult,
    AgentStatus,
    AgentTask,
    AgentType,
)


class BaseAgent:
    """Base deterministic agent."""

    def __init__(
        self,
        agent_type: AgentType,
    ) -> None:
        self.agent_type = agent_type

    def execute(
        self,
        task: AgentTask,
        evidence: Iterable[EvidenceBlock],
    ) -> AgentResult:
        """Execute a delegated task."""
        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status=AgentStatus.SUCCESS,
            evidence=tuple(evidence),
        )


class FailingAgent(BaseAgent):
    """Agent used to model an isolated execution failure."""

    def __init__(
        self,
        agent_type: AgentType,
        error: str = "agent execution failed",
    ) -> None:
        super().__init__(agent_type)
        self._error = error

    def execute(
        self,
        task: AgentTask,
        evidence: Iterable[EvidenceBlock],
    ) -> AgentResult:
        """Return a deterministic failure."""
        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status=AgentStatus.FAILED,
            evidence=(),
            error=self._error,
        )
