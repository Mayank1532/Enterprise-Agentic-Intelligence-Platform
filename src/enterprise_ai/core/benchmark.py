"""Deterministic benchmark dataset representations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    """One deterministic evaluation case."""

    case_id: str
    task: str
    expected_agent: str
    expected_tool: str
    expected_success: bool = True

    def __post_init__(self) -> None:
        """Validate benchmark case fields."""
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty.")

        if not self.task.strip():
            raise ValueError("task must not be empty.")

        if not self.expected_agent.strip():
            raise ValueError("expected_agent must not be empty.")

        if not self.expected_tool.strip():
            raise ValueError("expected_tool must not be empty.")


@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    """Immutable collection of benchmark cases."""

    name: str
    version: str
    cases: tuple[BenchmarkCase, ...]

    def __post_init__(self) -> None:
        """Validate benchmark dataset metadata."""
        if not self.name.strip():
            raise ValueError("benchmark name must not be empty.")

        if not self.version.strip():
            raise ValueError("benchmark version must not be empty.")

        case_ids = [case.case_id for case in self.cases]

        if len(case_ids) != len(set(case_ids)):
            raise ValueError("benchmark case IDs must be unique.")

    @property
    def size(self) -> int:
        """Return number of benchmark cases."""
        return len(self.cases)
