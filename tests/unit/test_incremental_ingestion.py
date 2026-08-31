"""Tests for incremental ingestion behavior."""

from enterprise_ai.common.incremental_ingestion import (
    IncrementalIngestionEngine,
)
from enterprise_ai.core.ingestion_state import (
    DocumentState,
    IngestionAction,
)


def test_new_document_is_created() -> None:
    engine = IncrementalIngestionEngine()

    decision = engine.apply("doc-1", "hash-1")

    assert decision.action is IngestionAction.CREATE
    assert decision.new_version == 1
    assert engine.state_size() == 1


def test_unchanged_document_is_skipped() -> None:
    engine = IncrementalIngestionEngine(
        [
            DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=3,
            )
        ]
    )

    decision = engine.apply("doc-1", "hash-1")

    assert decision.action is IngestionAction.SKIP
    assert decision.previous_version == 3
    assert decision.new_version is None

    state = engine.get_state("doc-1")
    assert state is not None
    assert state.version == 3


def test_changed_document_is_updated() -> None:
    engine = IncrementalIngestionEngine(
        [
            DocumentState(
                document_id="doc-1",
                content_hash="hash-1",
                version=3,
            )
        ]
    )

    decision = engine.apply("doc-1", "hash-2")

    assert decision.action is IngestionAction.UPDATE
    assert decision.previous_version == 3
    assert decision.new_version == 4

    state = engine.get_state("doc-1")
    assert state is not None
    assert state.content_hash == "hash-2"
    assert state.version == 4


def test_repeated_update_is_idempotent_for_same_content() -> None:
    engine = IncrementalIngestionEngine()

    first = engine.apply("doc-1", "hash-1")
    second = engine.apply("doc-1", "hash-1")
    third = engine.apply("doc-1", "hash-1")

    assert first.action is IngestionAction.CREATE
    assert second.action is IngestionAction.SKIP
    assert third.action is IngestionAction.SKIP

    state = engine.get_state("doc-1")
    assert state is not None
    assert state.version == 1


def test_multiple_documents_are_independent() -> None:
    engine = IncrementalIngestionEngine()

    first = engine.apply("doc-1", "hash-1")
    second = engine.apply("doc-2", "hash-2")

    assert first.action is IngestionAction.CREATE
    assert second.action is IngestionAction.CREATE
    assert engine.state_size() == 2
