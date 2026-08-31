"""Tests for deterministic ingestion batch contracts."""

from enterprise_ai.core.ingestion_batch import IngestionBatch
from enterprise_ai.core.ingestion_state import (
    IngestionAction,
    IngestionDecision,
)


def make_decision(
    action: IngestionAction,
    document_id: str,
) -> IngestionDecision:
    """Create a valid test decision."""
    if action is IngestionAction.CREATE:
        return IngestionDecision(
            action=action,
            document_id=document_id,
            previous_version=None,
            new_version=1,
        )

    if action is IngestionAction.UPDATE:
        return IngestionDecision(
            action=action,
            document_id=document_id,
            previous_version=1,
            new_version=2,
        )

    return IngestionDecision(
        action=action,
        document_id=document_id,
        previous_version=1,
        new_version=None,
    )


def test_empty_batch_is_valid() -> None:
    batch = IngestionBatch(decisions=())

    assert batch.size == 0
    assert batch.creates == 0
    assert batch.updates == 0
    assert batch.skips == 0


def test_batch_counts_decision_types() -> None:
    batch = IngestionBatch(
        decisions=(
            make_decision(IngestionAction.CREATE, "doc-1"),
            make_decision(IngestionAction.UPDATE, "doc-2"),
            make_decision(IngestionAction.SKIP, "doc-3"),
            make_decision(IngestionAction.CREATE, "doc-4"),
        )
    )

    assert batch.size == 4
    assert batch.creates == 2
    assert batch.updates == 1
    assert batch.skips == 1
