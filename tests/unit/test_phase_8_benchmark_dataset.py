"""Tests for the canonical Phase 8 benchmark dataset."""

from phase_8_benchmark_dataset import PHASE_8_BENCHMARK


def test_phase_8_benchmark_is_deterministic() -> None:
    assert PHASE_8_BENCHMARK.name == (
        "enterprise-agentic-intelligence-platform"
    )
    assert PHASE_8_BENCHMARK.version == "1.0"
    assert PHASE_8_BENCHMARK.size == 5


def test_phase_8_benchmark_case_ids_are_stable() -> None:
    assert tuple(
        case.case_id
        for case in PHASE_8_BENCHMARK.cases
    ) == (
        "routing-001",
        "routing-002",
        "routing-003",
        "routing-004",
        "routing-005",
    )

