"""Tests for incremental ingestion contracts."""

import pytest

from enterprise_ai.core.ingestion_state import (
    DocumentState,
    IngestionAction,
    IngestionDecision,
)


def test_document_state_is_valid() -> None:
    state = DocumentState(
        document_id="doc-1",
        content_hash="hash-1",
        version=1,
    )

    assert state.document_id == "doc-1"
    assert state.version == 1


def test_document_state_rejects_empty_document_id() -> None:
    with pytest.raises(ValueError, match="document_id"):
        DocumentState(
            document_id="",
            content_hash="hash",
            version=1,
        )


def test_document_state_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="version"):
        DocumentState(
            document_id="doc",
            content_hash="hash",
            version=0,
        )


def test_skip_decision_has_no_new_version() -> None:
    decision = IngestionDecision(
        action=IngestionAction.SKIP,
        document_id="doc-1",
        previous_version=2,
        new_version=None,
    )

    assert decision.action is IngestionAction.SKIP
    assert decision.new_version is None


def test_skip_decision_rejects_new_version() -> None:
    with pytest.raises(ValueError, match="skip"):
        IngestionDecision(
            action=IngestionAction.SKIP,
            document_id="doc-1",
            previous_version=2,
            new_version=3,
        )


def test_create_decision_requires_new_version() -> None:
    with pytest.raises(ValueError, match="new version"):
        IngestionDecision(
            action=IngestionAction.CREATE,
            document_id="doc-1",
            previous_version=None,
            new_version=None,
        )
