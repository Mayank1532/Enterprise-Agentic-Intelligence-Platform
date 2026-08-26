"""Deterministic bounded iterative workflow."""

from enterprise_ai.common.iteration_policy import (
    IterationPolicy,
    SequenceEvidenceProvider,
)
from enterprise_ai.common.structured_output_builder import (
    StructuredOutputBuilder,
)
from enterprise_ai.core.iterative_workflow import (
    IterationDecision,
    IterationState,
    IterationTermination,
    IterativeWorkflowResult,
)


class IterativeWorkflow:
    """Execute bounded iterations until completion or a hard limit."""

    def __init__(
        self,
        evidence_provider: SequenceEvidenceProvider,
        policy: IterationPolicy | None = None,
        max_iterations: int = 5,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")

        self._evidence_provider = evidence_provider
        self._policy = policy or IterationPolicy()
        self._max_iterations = max_iterations

    @property
    def max_iterations(self) -> int:
        """Return the hard iteration limit."""
        return self._max_iterations

    def run(
        self,
        query: str,
    ) -> IterativeWorkflowResult:
        """Execute bounded iterations deterministically."""
        evidence: tuple = ()
        iterations = 0

        while iterations < self._max_iterations:
            iterations += 1

            state = IterationState(
                query=query,
                iteration=iterations,
                evidence=evidence,
            )

            discovered = self._evidence_provider.get(
                iterations,
            )

            evidence = evidence + discovered

            state = IterationState(
                query=query,
                iteration=iterations,
                evidence=evidence,
            )

            decision = self._policy.evaluate(state)

            if decision.decision is IterationDecision.COMPLETE:
                output = StructuredOutputBuilder.supported(
                    answer=evidence[0].text,
                    confidence=1.0,
                    evidence=evidence,
                )

                return IterativeWorkflowResult(
                    query=query,
                    iterations=iterations,
                    termination=IterationTermination.COMPLETED,
                    evidence=evidence,
                    output=output,
                )

        output = StructuredOutputBuilder.refused(
            reason="maximum iterations reached without sufficient evidence",
        )

        return IterativeWorkflowResult(
            query=query,
            iterations=iterations,
            termination=IterationTermination.MAX_ITERATIONS,
            evidence=evidence,
            output=output,
        )
