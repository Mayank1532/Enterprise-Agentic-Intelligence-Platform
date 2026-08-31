"""Contracts for deterministic ingestion batches."""

from dataclasses import dataclass

from enterprise_ai.core.ingestion_state import IngestionDecision


@dataclass(frozen=True, slots=True)
class IngestionBatch:
    """Immutable collection of ingestion decisions."""

    decisions: tuple[IngestionDecision, ...]

    @property
    def size(self) -> int:
        """Return the number of decisions in the batch."""
        return len(self.decisions)

    @property
    def creates(self) -> int:
        """Return the number of create decisions."""
        return sum(
            decision.action.value == "create"
            for decision in self.decisions
        )

    @property
    def updates(self) -> int:
        """Return the number of update decisions."""
        return sum(
            decision.action.value == "update"
            for decision in self.decisions
        )

    @property
    def skips(self) -> int:
        """Return the number of skip decisions."""
        return sum(
            decision.action.value == "skip"
            for decision in self.decisions
        )
