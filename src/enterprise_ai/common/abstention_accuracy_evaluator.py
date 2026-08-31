"""Abstention accuracy evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AbstentionAccuracyEvaluator:
    """Evaluate whether the system abstains when it should."""

    def evaluate(
        self,
        expected_abstentions: tuple[bool, ...],
        actual_abstentions: tuple[bool, ...],
    ) -> float:
        """Return the fraction of abstention decisions that are correct."""
        if len(expected_abstentions) != len(actual_abstentions):
            raise ValueError(
                "expected and actual abstention sequences must have equal length."
            )

        if not expected_abstentions:
            return 1.0

        correct = sum(
            expected == actual
            for expected, actual in zip(
                expected_abstentions,
                actual_abstentions,
                strict=True,
            )
        )

        return correct / len(expected_abstentions)
