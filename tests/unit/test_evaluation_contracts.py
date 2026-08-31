"""Tests for Phase 8 canonical evaluation contracts."""

import pytest

from enterprise_ai.core.agent_tool_selection import AgentToolSelectionOutcome
from enterprise_ai.core.benchmark_dataset import BenchmarkDataset
from enterprise_ai.core.evaluation_case import EvaluationCase
from enterprise_ai.core.evaluation_dimension import EvaluationDimension
from enterprise_ai.core.evaluation_outcome import EvaluationOutcome
from enterprise_ai.core.performance_measurement import PerformanceMeasurement
from enterprise_ai.core.task_outcome import TaskOutcome


def test_evaluation_case_preserves_expected_targets() -> None:
    case = EvaluationCase(
        case_id="case-1",
        query="What is the answer?",
        expected_evidence_ids=("e1", "e2"),
        expected_agent="research",
        expected_tool="search",
        expected_success=True,
        expected_abstention=False,
    )

    assert case.case_id == "case-1"
    assert case.expected_evidence_ids == ("e1", "e2")
    assert case.expected_agent == "research"
    assert case.expected_tool == "search"


def test_evaluation_dimension_contains_phase_8_metrics() -> None:
    assert EvaluationDimension.RETRIEVAL_RECALL.value == "retrieval_recall"
    assert EvaluationDimension.RETRIEVAL_PRECISION.value == "retrieval_precision"
    assert EvaluationDimension.RERANKER_EFFECTIVENESS.value == "reranker_effectiveness"
    assert EvaluationDimension.GROUNDEDNESS.value == "groundedness"
    assert EvaluationDimension.FAITHFULNESS.value == "faithfulness"
    assert EvaluationDimension.CITATION_CORRECTNESS.value == "citation_correctness"
    assert EvaluationDimension.UNSUPPORTED_CLAIM_RATE.value == "unsupported_claim_rate"
    assert EvaluationDimension.ABSTENTION_ACCURACY.value == "abstention_accuracy"
    assert EvaluationDimension.AGENT_TOOL_SELECTION.value == "agent_tool_selection"
    assert EvaluationDimension.TASK_SUCCESS.value == "task_success"
    assert EvaluationDimension.LATENCY.value == "latency"
    assert EvaluationDimension.THROUGHPUT.value == "throughput"
    assert EvaluationDimension.FAILURE_RATE.value == "failure_rate"


def test_evaluation_outcome_accepts_normalized_value() -> None:
    outcome = EvaluationOutcome(
        dimension=EvaluationDimension.GROUNDEDNESS,
        value=0.95,
        passed=True,
        case_id="case-1",
    )

    assert outcome.value == 0.95
    assert outcome.passed is True


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_evaluation_outcome_rejects_invalid_value(value: float) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        EvaluationOutcome(
            dimension=EvaluationDimension.GROUNDEDNESS,
            value=value,
            passed=False,
        )


def test_benchmark_dataset_enforces_unique_case_ids() -> None:
    case = EvaluationCase(
        case_id="duplicate",
        query="test",
    )

    with pytest.raises(ValueError, match="unique"):
        BenchmarkDataset(
            name="baseline",
            version="1.0",
            cases=(case, case),
        )


def test_benchmark_dataset_reports_size() -> None:
    dataset = BenchmarkDataset(
        name="baseline",
        version="1.0",
        cases=(
            EvaluationCase(case_id="case-1", query="one"),
            EvaluationCase(case_id="case-2", query="two"),
        ),
    )

    assert dataset.size == 2


def test_performance_measurement_preserves_values() -> None:
    measurement = PerformanceMeasurement(
        latency_seconds=0.25,
        throughput=4.0,
        failed=False,
    )

    assert measurement.latency_seconds == 0.25
    assert measurement.throughput == 4.0
    assert measurement.failed is False


def test_agent_tool_selection_preserves_observation() -> None:
    outcome = AgentToolSelectionOutcome(
        case_id="case-1",
        selected_agent="research",
        selected_tool="search",
        correct=True,
    )

    assert outcome.selected_agent == "research"
    assert outcome.selected_tool == "search"
    assert outcome.correct is True


def test_task_outcome_preserves_result() -> None:
    outcome = TaskOutcome(
        case_id="case-1",
        succeeded=True,
        failed=False,
        abstained=False,
    )

    assert outcome.succeeded is True
    assert outcome.failed is False
    assert outcome.abstained is False


def test_task_outcome_rejects_success_and_failure() -> None:
    with pytest.raises(ValueError, match="both succeeded and failed"):
        TaskOutcome(
            case_id="case-1",
            succeeded=True,
            failed=True,
            abstained=False,
        )


def test_task_outcome_rejects_successful_abstention() -> None:
    with pytest.raises(ValueError, match="cannot be abstained"):
        TaskOutcome(
            case_id="case-1",
            succeeded=True,
            failed=False,
            abstained=True,
        )
