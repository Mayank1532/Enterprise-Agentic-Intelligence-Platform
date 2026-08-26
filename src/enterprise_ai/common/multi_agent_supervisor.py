"""Deterministic multi-agent supervisor."""

from collections.abc import Mapping, Sequence

from enterprise_ai.common.multi_agent import BaseAgent
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import (
    AgentResult,
    AgentStatus,
    AgentTask,
    AgentType,
    SupervisorResult,
    SupervisorStatus,
)


class MultiAgentSupervisor:
    """Delegate tasks and aggregate agent results deterministically."""

    def __init__(
        self,
        agents: Mapping[AgentType, BaseAgent],
    ) -> None:
        if not agents:
            raise ValueError("Supervisor requires at least one agent.")

        self._agents = dict(agents)

    def run(
        self,
        query: str,
        tasks: Sequence[AgentTask],
        evidence_by_task: Mapping[
            str,
            Sequence[EvidenceBlock],
        ],
    ) -> SupervisorResult:
        """Execute delegated tasks and aggregate results."""
        if not tasks:
            raise ValueError("Supervisor requires at least one task.")

        results: list[AgentResult] = []

        for task in tasks:
            agent = self._agents.get(task.agent_type)

            if agent is None:
                results.append(
                    AgentResult(
                        task_id=task.task_id,
                        agent_type=task.agent_type,
                        status=AgentStatus.FAILED,
                        evidence=(),
                        error="agent is not registered",
                    )
                )
                continue

            result = agent.execute(
                task,
                evidence_by_task.get(
                    task.task_id,
                    (),
                ),
            )

            results.append(result)

        successful = sum(result.status is AgentStatus.SUCCESS for result in results)

        if successful == len(results):
            status = SupervisorStatus.SUCCESS
        elif successful > 0:
            status = SupervisorStatus.PARTIAL
        else:
            status = SupervisorStatus.FAILED

        merged_evidence = tuple(evidence for result in results for evidence in result.evidence)

        return SupervisorResult(
            query=query,
            status=status,
            agent_results=tuple(results),
            evidence=merged_evidence,
        )
