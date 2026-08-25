"""Deterministic retrieval evaluation representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationMetric:
    """One named evaluation metric."""

    name: str
    value: float
    passed: bool

    def __post_init__(self) -> None:
        """Validate metric values."""
        if not self.name.strip():
            raise ValueError("metric name must not be empty")

        if not 0.0 <= self.value <= 1.0:
            raise ValueError("metric value must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Final deterministic retrieval evaluation report."""

    metrics: tuple[EvaluationMetric, ...]

    @property
    def passed(self) -> bool:
        """Return whether every metric passed."""
        return bool(self.metrics) and all(metric.passed for metric in self.metrics)
