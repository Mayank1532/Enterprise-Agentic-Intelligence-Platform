"""Tests for agent/tool selection accuracy."""

import pytest

from enterprise_ai.common.agent_tool_selection_accuracy_evaluator import (
    AgentToolSelectionAccuracyEvaluator,
)


def test_all_selections_correct() -> None:
    evaluator = AgentToolSelectionAccuracyEvaluator()

    assert evaluator.evaluate(
        ("retrieval", "live_data", "mcp"),
        ("retrieval", "live_data", "mcp"),
    ) == 1.0


def test_partial_selection_accuracy() -> None:
    evaluator = AgentToolSelectionAccuracyEvaluator()

    result = evaluator.evaluate(
        ("retrieval", "live_data", "mcp", "a2a"),
        ("retrieval", "mcp", "mcp", "a2a"),
    )

    assert result == pytest.approx(0.75)


def test_empty_selection_is_perfect() -> None:
    evaluator = AgentToolSelectionAccuracyEvaluator()

    assert evaluator.evaluate((), ()) == 1.0


def test_length_mismatch_is_rejected() -> None:
    evaluator = AgentToolSelectionAccuracyEvaluator()

    with pytest.raises(
        ValueError,
        match="equal length",
    ):
        evaluator.evaluate(
            ("retrieval",),
            (),
        )
