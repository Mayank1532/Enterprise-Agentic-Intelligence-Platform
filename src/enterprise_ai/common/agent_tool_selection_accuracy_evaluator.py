"""Agent and tool selection accuracy evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentToolSelectionAccuracyEvaluator:
    """Evaluate exact-match accuracy of agent/tool selections."""

    def evaluate(
        self,
        expected: tuple[str, ...],
        actual: tuple[str, ...],
    ) -> float:
        """Return the fraction of selections that exactly match."""
        if len(expected) != len(actual):
            raise ValueError(
                "expected and actual selections must have equal length."
            )

        if not expected:
            return 1.0

        correct = sum(
            expected_item == actual_item
            for expected_item, actual_item in zip(
                expected,
                actual,
                strict=True,
            )
        )

        return correct / len(expected)
