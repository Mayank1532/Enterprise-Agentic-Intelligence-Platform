"""Deterministic iteration policy."""

from collections.abc import Sequence

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.iterative_workflow import (
    IterationDecision,
    IterationResult,
    IterationState,
)


class IterationPolicy:
    """Determine whether another iteration is required."""

    def evaluate(
        self,
        state: IterationState,
    ) -> IterationResult:
        """Complete when evidence is available."""
        if state.has_evidence:
            return IterationResult(
                decision=IterationDecision.COMPLETE,
                evidence=state.evidence,
            )

        return IterationResult(
            decision=IterationDecision.CONTINUE,
            evidence=(),
        )


class SequenceEvidenceProvider:
    """Provide predetermined evidence for each iteration."""

    def __init__(
        self,
        evidence_by_iteration: Sequence[Sequence[EvidenceBlock]],
    ) -> None:
        self._evidence_by_iteration = tuple(tuple(items) for items in evidence_by_iteration)

    def get(
        self,
        iteration: int,
    ) -> tuple[EvidenceBlock, ...]:
        """Return evidence assigned to an iteration."""
        index = iteration - 1

        if index < 0:
            raise ValueError("Iteration must be greater than zero.")

        if index >= len(self._evidence_by_iteration):
            return ()

        return self._evidence_by_iteration[index]
