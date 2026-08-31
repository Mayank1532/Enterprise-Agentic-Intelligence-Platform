"""Benchmark regression evaluation."""

from dataclasses import dataclass

from enterprise_ai.core.benchmark import BenchmarkDataset


@dataclass(frozen=True, slots=True)
class BenchmarkEvaluationResult:
    """Deterministic benchmark evaluation result."""

    dataset_name: str
    dataset_version: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float

    def __post_init__(self) -> None:
        """Validate result invariants."""
        if self.total_cases < 0:
            raise ValueError("total_cases must not be negative.")

        if self.passed_cases < 0:
            raise ValueError("passed_cases must not be negative.")

        if self.failed_cases < 0:
            raise ValueError("failed_cases must not be negative.")

        if self.passed_cases + self.failed_cases != self.total_cases:
            raise ValueError(
                "passed_cases + failed_cases must equal total_cases."
            )

        if not 0.0 <= self.pass_rate <= 1.0:
            raise ValueError("pass_rate must be between 0 and 1.")


@dataclass(frozen=True, slots=True)
class BenchmarkRegressionEvaluator:
    """Evaluate deterministic benchmark regression outcomes."""

    def evaluate(
        self,
        dataset: BenchmarkDataset,
        actual_agents: tuple[str, ...],
        actual_tools: tuple[str, ...],
        actual_success: tuple[bool, ...],
    ) -> BenchmarkEvaluationResult:
        """Evaluate actual execution results against benchmark expectations."""
        expected_cases = dataset.cases

        if not (
            len(actual_agents)
            == len(actual_tools)
            == len(actual_success)
            == len(expected_cases)
        ):
            raise ValueError(
                "actual result collections must match dataset size."
            )

        passed = 0

        for case, actual_agent, actual_tool, actual_ok in zip(
            expected_cases,
            actual_agents,
            actual_tools,
            actual_success,
            strict=True,
        ):
            if (
                case.expected_agent == actual_agent
                and case.expected_tool == actual_tool
                and case.expected_success == actual_ok
            ):
                passed += 1

        total = dataset.size
        failed = total - passed
        pass_rate = 1.0 if total == 0 else passed / total

        return BenchmarkEvaluationResult(
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            pass_rate=pass_rate,
        )
