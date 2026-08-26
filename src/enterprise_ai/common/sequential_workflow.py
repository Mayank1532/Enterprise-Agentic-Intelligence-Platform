"""Deterministic sequential workflow steps."""

from collections.abc import Iterable

from enterprise_ai.common.structured_output_builder import (
    StructuredOutputBuilder,
)
from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.workflow import WorkflowState


class EvidenceStep:
    """Attach deterministic evidence to workflow state."""

    def execute(
        self,
        state: WorkflowState,
        evidence: Iterable[EvidenceBlock],
    ) -> WorkflowState:
        """Return state containing ordered evidence."""
        return WorkflowState(
            query=state.query,
            evidence=tuple(evidence),
            output=state.output,
        )


class StructuredOutputStep:
    """Convert workflow evidence into structured output."""

    def execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        """Build supported output when evidence exists."""
        if not state.has_evidence:
            return WorkflowState(
                query=state.query,
                evidence=state.evidence,
                output=StructuredOutputBuilder.refused(
                    reason="insufficient evidence",
                ),
            )

        first_evidence = state.evidence[0]

        output = StructuredOutputBuilder.supported(
            answer=first_evidence.text,
            confidence=1.0,
            evidence=state.evidence,
        )

        return WorkflowState(
            query=state.query,
            evidence=state.evidence,
            output=output,
        )


class WorkflowValidationStep:
    """Validate the final sequential workflow state."""

    def execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        """Reject impossible workflow output states."""
        if state.output is None:
            raise ValueError("Workflow completed without structured output.")

        if state.output.status == "supported":
            if not state.evidence:
                raise ValueError("Supported workflow output requires evidence.")

            if not state.output.result.evidence:
                raise ValueError("Supported workflow output requires evidence references.")

        if state.output.status == "refused":
            if state.output.result.supported:
                raise ValueError("Refused workflow output cannot be supported.")

        return state


class SequentialWorkflow:
    """Execute workflow steps deterministically in order."""

    def __init__(
        self,
        evidence_step: EvidenceStep | None = None,
        output_step: StructuredOutputStep | None = None,
        validation_step: WorkflowValidationStep | None = None,
    ) -> None:
        self._evidence_step = evidence_step or EvidenceStep()
        self._output_step = output_step or StructuredOutputStep()
        self._validation_step = validation_step or WorkflowValidationStep()

    def run(
        self,
        query: str,
        evidence: Iterable[EvidenceBlock],
    ) -> WorkflowState:
        """Execute the complete sequential workflow."""
        state = WorkflowState(query=query)

        state = self._evidence_step.execute(
            state,
            evidence,
        )

        state = self._output_step.execute(state)

        state = self._validation_step.execute(state)

        return state
