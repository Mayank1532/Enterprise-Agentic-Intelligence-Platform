"""Tests for deterministic batch ingestion planning."""

import pytest

from enterprise_ai.common.batch_ingestion import BatchIngestionPlanner
from enterprise_ai.core.ingestion_state import (
    DocumentState,
    IngestionAction,
)


def test_documents_are_split_into_deterministic_batches() -> None:
    planner = BatchIngestionPlanner()

    batches = planner.plan(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-3", "hash-3"),
            ("doc-4", "hash-4"),
            ("doc-5", "hash-5"),
        ),
        batch_size=2,
    )

    assert len(batches) == 3
    assert [batch.size for batch in batches] == [2, 2, 1]


def test_batch_order_matches_input_order() -> None:
    planner = BatchIngestionPlanner()

    batches = planner.plan(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-3", "hash-3"),
        ),
        batch_size=2,
    )

    ids = tuple(
        decision.document_id
        for batch in batches
        for decision in batch.decisions
    )

    assert ids == ("doc-1", "doc-2", "doc-3")


def test_existing_state_is_used_for_batch_decisions() -> None:
    planner = BatchIngestionPlanner(
        existing_state=(
            DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=4,
            ),
        )
    )

    batches = planner.plan(
        documents=(
            ("doc-1", "hash-1"),
            ("doc-2", "hash-2"),
            ("doc-1", "hash-2"),
        ),
        batch_size=10,
    )

    decisions = batches[0].decisions

    assert decisions[0].action is IngestionAction.SKIP
    assert decisions[1].action is IngestionAction.CREATE
    assert decisions[2].action is IngestionAction.UPDATE


def test_batch_size_must_be_positive() -> None:
    planner = BatchIngestionPlanner()

    with pytest.raises(ValueError, match="batch_size"):
        planner.plan(
            documents=(("doc-1", "hash-1"),),
            batch_size=0,
        )


def test_empty_input_produces_no_batches() -> None:
    planner = BatchIngestionPlanner()

    batches = planner.plan(
        documents=(),
        batch_size=10,
    )

    assert batches == ()


def test_single_document_batch() -> None:
    planner = BatchIngestionPlanner()

    batches = planner.plan(
        documents=(("doc-1", "hash-1"),),
        batch_size=1,
    )

    assert len(batches) == 1
    assert batches[0].size == 1
    assert batches[0].decisions[0].action is IngestionAction.CREATE
