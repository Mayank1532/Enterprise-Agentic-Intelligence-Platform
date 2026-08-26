"""Tests for sequential workflow execution order."""

from collections.abc import Iterable

from enterprise_ai.common.sequential_workflow import (
    EvidenceStep,
    SequentialWorkflow,
    StructuredOutputStep,
    WorkflowState,
    WorkflowValidationStep,
)
from enterprise_ai.core.evidence import EvidenceBlock


def test_steps_execute_in_declared_order() -> None:
    """Workflow executes evidence, output, then validation."""
    calls: list[str] = []

    class TrackingEvidenceStep(EvidenceStep):
        def execute(
            self,
            state: WorkflowState,
            evidence: Iterable[EvidenceBlock],
        ) -> WorkflowState:
            calls.append("evidence")
            return super().execute(state, evidence)

    class TrackingOutputStep(StructuredOutputStep):
        def execute(
            self,
            state: WorkflowState,
        ) -> WorkflowState:
            calls.append("output")
            return super().execute(state)

    class TrackingValidationStep(WorkflowValidationStep):
        def execute(
            self,
            state: WorkflowState,
        ) -> WorkflowState:
            calls.append("validation")
            return super().execute(state)

    workflow = SequentialWorkflow(
        evidence_step=TrackingEvidenceStep(),
        output_step=TrackingOutputStep(),
        validation_step=TrackingValidationStep(),
    )

    workflow.run(
        query="order",
        evidence=(),
    )

    assert calls == [
        "evidence",
        "output",
        "validation",
    ]
