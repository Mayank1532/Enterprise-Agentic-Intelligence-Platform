"""Tests for deterministic multi-agent orchestration."""

import pytest

from enterprise_ai.common.multi_agent import (
    BaseAgent,
    FailingAgent,
)
from enterprise_ai.common.multi_agent_supervisor import (
    MultiAgentSupervisor,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import (
    AgentStatus,
    AgentTask,
    AgentType,
    SupervisorStatus,
)


def make_evidence(
    evidence_id: str,
    text: str,
) -> EvidenceBlock:
    """Create deterministic evidence."""
    return EvidenceBlock(
        evidence_id=evidence_id,
        document_id=f"document-{evidence_id}",
        chunk_id=f"chunk-{evidence_id}",
        source_path="document.txt",
        chunk_index=0,
        text=text,
    )


def make_tasks() -> tuple[AgentTask, ...]:
    """Create deterministic agent tasks."""
    return (
        AgentTask(
            task_id="task-document",
            agent_type=AgentType.DOCUMENT,
            query="document research",
        ),
        AgentTask(
            task_id="task-web",
            agent_type=AgentType.WEB,
            query="web research",
        ),
    )


def test_supervisor_requires_agents() -> None:
    """Supervisor cannot operate without agents."""
    with pytest.raises(
        ValueError,
        match="at least one agent",
    ):
        MultiAgentSupervisor({})


def test_supervisor_requires_tasks() -> None:
    """Supervisor cannot operate without delegated tasks."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(AgentType.DOCUMENT),
        }
    )

    with pytest.raises(
        ValueError,
        match="at least one task",
    ):
        supervisor.run(
            query="test",
            tasks=(),
            evidence_by_task={},
        )


def test_all_agents_success() -> None:
    """All successful agents produce overall success."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(AgentType.DOCUMENT),
            AgentType.WEB: BaseAgent(AgentType.WEB),
        }
    )

    result = supervisor.run(
        query="research",
        tasks=make_tasks(),
        evidence_by_task={
            "task-document": (
                make_evidence(
                    "evidence-document",
                    "document result",
                ),
            ),
            "task-web": (
                make_evidence(
                    "evidence-web",
                    "web result",
                ),
            ),
        },
    )

    assert result.status is SupervisorStatus.SUCCESS
    assert result.successful_agents == 2
    assert result.failed_agents == 0
    assert len(result.evidence) == 2


def test_partial_agent_failure_preserves_successful_evidence() -> None:
    """One failed agent must not discard another agent's evidence."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(AgentType.DOCUMENT),
            AgentType.WEB: FailingAgent(
                AgentType.WEB,
                error="web unavailable",
            ),
        }
    )

    result = supervisor.run(
        query="research",
        tasks=make_tasks(),
        evidence_by_task={
            "task-document": (
                make_evidence(
                    "evidence-document",
                    "successful document evidence",
                ),
            ),
            "task-web": (),
        },
    )

    assert result.status is SupervisorStatus.PARTIAL
    assert result.successful_agents == 1
    assert result.failed_agents == 1

    assert result.evidence == (
        make_evidence(
            "evidence-document",
            "successful document evidence",
        ),
    )

    failed = result.agent_results[1]

    assert failed.status is AgentStatus.FAILED
    assert failed.error == "web unavailable"


def test_all_agents_fail() -> None:
    """All failed agents produce overall failure."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: FailingAgent(
                AgentType.DOCUMENT,
            ),
            AgentType.WEB: FailingAgent(
                AgentType.WEB,
            ),
        }
    )

    result = supervisor.run(
        query="failure",
        tasks=make_tasks(),
        evidence_by_task={},
    )

    assert result.status is SupervisorStatus.FAILED
    assert result.successful_agents == 0
    assert result.failed_agents == 2
    assert result.evidence == ()


def test_unregistered_agent_isolated_as_failure() -> None:
    """Unknown agent types become explicit task failures."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(
                AgentType.DOCUMENT,
            ),
        }
    )

    tasks = (
        AgentTask(
            task_id="task-document",
            agent_type=AgentType.DOCUMENT,
            query="document",
        ),
        AgentTask(
            task_id="task-web",
            agent_type=AgentType.WEB,
            query="web",
        ),
    )

    result = supervisor.run(
        query="unknown agent",
        tasks=tasks,
        evidence_by_task={
            "task-document": (
                make_evidence(
                    "evidence-document",
                    "document evidence",
                ),
            ),
        },
    )

    assert result.status is SupervisorStatus.PARTIAL
    assert result.successful_agents == 1
    assert result.failed_agents == 1

    assert result.agent_results[1].error == ("agent is not registered")


def test_agent_results_preserve_task_order() -> None:
    """Supervisor aggregation preserves delegated task order."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(
                AgentType.DOCUMENT,
            ),
            AgentType.WEB: BaseAgent(
                AgentType.WEB,
            ),
        }
    )

    tasks = make_tasks()

    result = supervisor.run(
        query="ordering",
        tasks=tasks,
        evidence_by_task={
            "task-document": (),
            "task-web": (),
        },
    )

    assert [item.task_id for item in result.agent_results] == [
        "task-document",
        "task-web",
    ]


def test_agent_result_preserves_agent_identity() -> None:
    """Agent results retain the canonical agent type."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(
                AgentType.DOCUMENT,
            ),
        }
    )

    task = AgentTask(
        task_id="task-document",
        agent_type=AgentType.DOCUMENT,
        query="document",
    )

    result = supervisor.run(
        query="identity",
        tasks=(task,),
        evidence_by_task={},
    )

    assert result.agent_results[0].agent_type is (AgentType.DOCUMENT)
