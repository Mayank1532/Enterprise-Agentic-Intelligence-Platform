"""Task success rate evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskSuccessRateEvaluator:
    """Evaluate the proportion of successfully completed tasks."""

    def evaluate(
        self,
        successful: tuple[bool, ...],
    ) -> float:
        """Return the fraction of successful tasks."""
        if not successful:
            return 1.0

        return sum(successful) / len(successful)
