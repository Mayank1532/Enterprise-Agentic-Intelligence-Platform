"""Tests for multi-agent evidence-backed output."""

from enterprise_ai.common.multi_agent import (
    BaseAgent,
    FailingAgent,
)
from enterprise_ai.common.multi_agent_output import (
    MultiAgentOutputCoordinator,
)
from enterprise_ai.common.multi_agent_supervisor import (
    MultiAgentSupervisor,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.multi_agent import (
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
    """Create deterministic delegated tasks."""
    return (
        AgentTask(
            task_id="document-task",
            agent_type=AgentType.DOCUMENT,
            query="document research",
        ),
        AgentTask(
            task_id="web-task",
            agent_type=AgentType.WEB,
            query="web research",
        ),
    )


def test_successful_multi_agent_result_becomes_supported_output() -> None:
    """Successful evidence produces supported structured output."""
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

    result = supervisor.run(
        query="research",
        tasks=make_tasks(),
        evidence_by_task={
            "document-task": (
                make_evidence(
                    "document-001",
                    "Verified document evidence.",
                ),
            ),
            "web-task": (
                make_evidence(
                    "web-001",
                    "Verified web evidence.",
                ),
            ),
        },
    )

    final = MultiAgentOutputCoordinator().build(result)

    assert result.status is SupervisorStatus.SUCCESS
    assert final.output.status == "supported"
    assert final.evidence == result.evidence
    assert tuple(reference.evidence_id for reference in final.output.result.evidence) == tuple(
        evidence.evidence_id for evidence in result.evidence
    )


def test_partial_failure_preserves_successful_evidence_in_output() -> None:
    """Partial failure must preserve successful evidence."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(
                AgentType.DOCUMENT,
            ),
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
            "document-task": (
                make_evidence(
                    "document-001",
                    "Verified document evidence.",
                ),
            ),
            "web-task": (),
        },
    )

    final = MultiAgentOutputCoordinator().build(result)

    assert result.status is SupervisorStatus.PARTIAL
    assert final.output.status == "supported"
    assert final.evidence == (
        make_evidence(
            "document-001",
            "Verified document evidence.",
        ),
    )
    assert "Some delegated agents failed" in final.output.result.answer


def test_no_evidence_produces_explicit_refusal() -> None:
    """No verified evidence must produce refusal."""
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
        query="unsupported",
        tasks=make_tasks(),
        evidence_by_task={},
    )

    final = MultiAgentOutputCoordinator().build(result)

    assert result.status is SupervisorStatus.FAILED
    assert final.output.status == "refused"
    assert final.evidence == ()
    assert final.output.result.evidence == ()


def test_output_uses_only_aggregated_evidence() -> None:
    """Final output evidence must exactly match supervisor evidence."""
    supervisor = MultiAgentSupervisor(
        {
            AgentType.DOCUMENT: BaseAgent(
                AgentType.DOCUMENT,
            ),
        }
    )

    task = AgentTask(
        task_id="document-task",
        agent_type=AgentType.DOCUMENT,
        query="document",
    )

    result = supervisor.run(
        query="evidence",
        tasks=(task,),
        evidence_by_task={
            "document-task": (
                make_evidence(
                    "document-001",
                    "Canonical evidence.",
                ),
            ),
        },
    )

    final = MultiAgentOutputCoordinator().build(result)

    assert tuple(reference.evidence_id for reference in final.output.result.evidence) == tuple(
        evidence.evidence_id for evidence in result.evidence
    )
    assert final.evidence is result.evidence
