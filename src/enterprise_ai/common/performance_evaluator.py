"""Latency, throughput, and failure-rate evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerformanceEvaluator:
    """Evaluate runtime performance measurements."""

    def latency(self, durations_seconds: tuple[float, ...]) -> float:
        """Return mean latency in seconds."""
        if not durations_seconds:
            return 0.0

        if any(duration < 0.0 for duration in durations_seconds):
            raise ValueError("latency values must not be negative.")

        return sum(durations_seconds) / len(durations_seconds)

    def throughput(
        self,
        completed_items: int,
        duration_seconds: float,
    ) -> float:
        """Return completed items per second."""
        if completed_items < 0:
            raise ValueError("completed_items must not be negative.")

        if duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be greater than zero.")

        return completed_items / duration_seconds

    def failure_rate(
        self,
        failed_items: int,
        total_items: int,
    ) -> float:
        """Return the fraction of failed items."""
        if failed_items < 0:
            raise ValueError("failed_items must not be negative.")

        if total_items < 0:
            raise ValueError("total_items must not be negative.")

        if failed_items > total_items:
            raise ValueError(
                "failed_items must not exceed total_items."
            )

        if total_items == 0:
            return 0.0

        return failed_items / total_items
