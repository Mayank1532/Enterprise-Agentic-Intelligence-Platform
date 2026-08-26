"""Tests for multi-agent execution isolation."""

from collections.abc import Iterable

from enterprise_ai.common.multi_agent import BaseAgent
from enterprise_ai.common.multi_agent_supervisor import (
    MultiAgentSupervisor,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import (
    AgentResult,
    AgentTask,
    AgentType,
)


class TrackingAgent(BaseAgent):
    """Agent that records delegated tasks."""

    def __init__(
        self,
        agent_type: AgentType,
        observed: list[tuple[AgentType, str]],
    ) -> None:
        super().__init__(agent_type)
        self._observed = observed

    def execute(
        self,
        task: AgentTask,
        evidence: Iterable[EvidenceBlock],
    ) -> AgentResult:
        """Record task and delegate to base implementation."""
        self._observed.append(
            (
                self.agent_type,
                task.task_id,
            )
        )

        return super().execute(
            task,
            evidence,
        )


def test_agents_receive_only_their_own_task() -> None:
    """Each agent receives its explicitly delegated task."""
    observed: list[tuple[AgentType, str]] = []

    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: TrackingAgent(
                AgentType.DOCUMENT,
                observed,
            ),
            AgentType.WEB: TrackingAgent(
                AgentType.WEB,
                observed,
            ),
        }
    )

    tasks = (
        AgentTask(
            task_id="document-task",
            agent_type=AgentType.DOCUMENT,
            query="documents",
        ),
        AgentTask(
            task_id="web-task",
            agent_type=AgentType.WEB,
            query="web",
        ),
    )

    supervisor.run(
        query="isolation",
        tasks=tasks,
        evidence_by_task={},
    )

    assert observed == [
        (AgentType.DOCUMENT, "document-task"),
        (AgentType.WEB, "web-task"),
    ]
