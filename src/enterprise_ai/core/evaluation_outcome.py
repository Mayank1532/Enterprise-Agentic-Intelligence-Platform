"""Canonical evaluation outcome contract."""

from dataclasses import dataclass

from enterprise_ai.core.evaluation_dimension import EvaluationDimension


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    """One measured evaluation result."""

    dimension: EvaluationDimension
    value: float
    passed: bool
    case_id: str | None = None

    def __post_init__(self) -> None:
        """Validate normalized evaluation values."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("evaluation value must be between 0 and 1.")

        if self.case_id is not None and not self.case_id.strip():
            raise ValueError("case_id must not be empty when provided.")
