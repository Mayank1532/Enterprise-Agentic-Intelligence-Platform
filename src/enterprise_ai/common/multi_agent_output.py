"""Build structured output from aggregated multi-agent evidence."""

from enterprise_ai.common.structured_output_builder import (
    StructuredOutputBuilder,
)
from enterprise_ai.core.multi_agent import (
    SupervisorResult,
    SupervisorStatus,
)
from enterprise_ai.core.multi_agent_output import MultiAgentOutput


class MultiAgentOutputCoordinator:
    """Convert supervisor results into evidence-backed output."""

    def build(
        self,
        result: SupervisorResult,
    ) -> MultiAgentOutput:
        """Build deterministic structured output."""
        if not result.evidence:
            output = StructuredOutputBuilder.refused(
                reason=("no verified evidence available from the delegated agents"),
            )

            return MultiAgentOutput(
                result=result,
                output=output,
                evidence=(),
            )

        answer = result.evidence[0].text

        if result.status is SupervisorStatus.PARTIAL:
            answer = (
                f"{answer} "
                "Some delegated agents failed; "
                "the response uses only successful evidence."
            )

        output = StructuredOutputBuilder.supported(
            answer=answer,
            confidence=1.0,
            evidence=result.evidence,
        )

        return MultiAgentOutput(
            result=result,
            output=output,
            evidence=result.evidence,
        )
