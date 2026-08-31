"""Performance measurement contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PerformanceMeasurement:
    """Normalized performance observation."""

    latency_seconds: float
    throughput: float
    failed: bool

    def __post_init__(self) -> None:
        """Validate performance values."""
        if self.latency_seconds < 0.0:
            raise ValueError("latency_seconds must be non-negative.")

        if self.throughput < 0.0:
            raise ValueError("throughput must be non-negative.")
