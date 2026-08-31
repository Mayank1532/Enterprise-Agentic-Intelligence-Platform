"""Deterministic benchmark dataset contract."""

from dataclasses import dataclass

from enterprise_ai.core.evaluation_case import EvaluationCase


@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    """Named collection of deterministic evaluation cases."""

    name: str
    version: str
    cases: tuple[EvaluationCase, ...]

    def __post_init__(self) -> None:
        """Validate benchmark identity and cases."""
        if not self.name.strip():
            raise ValueError("benchmark name must not be empty.")

        if not self.version.strip():
            raise ValueError("benchmark version must not be empty.")

        case_ids = [case.case_id for case in self.cases]

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("benchmark case IDs must be unique.")

    @property
    def size(self) -> int:
        """Return the number of benchmark cases."""
        return len(self.cases)
