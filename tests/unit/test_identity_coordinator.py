"""Tests for identity-aware ingestion coordination."""

from pathlib import Path

from enterprise_ai.identity.coordinator import (
    IdentityAwareIngestionCoordinator,
)
from enterprise_ai.identity.persistent_registry import (
    PersistentDocumentIdentityRegistry,
)
from enterprise_ai.identity.registry import IdentityStatus


def build_coordinator(
    store_path: Path,
) -> IdentityAwareIngestionCoordinator:
    """Build an isolated coordinator."""
    registry = PersistentDocumentIdentityRegistry(store_path)
    return IdentityAwareIngestionCoordinator(registry)


def test_classify_new_document(tmp_path: Path) -> None:
    """A previously unseen document is classified as new."""
    document = tmp_path / "document.txt"
    document.write_text("evidence", encoding="utf-8")

    coordinator = build_coordinator(
        tmp_path / "metadata" / "identity.json",
    )

    decision = coordinator.classify(document)

    assert decision.status == IdentityStatus.NEW
    assert decision.version == 1


def test_classify_same_document_as_duplicate(tmp_path: Path) -> None:
    """Repeated ingestion of unchanged content is a duplicate."""
    document = tmp_path / "document.txt"
    document.write_text("evidence", encoding="utf-8")

    store_path = tmp_path / "metadata" / "identity.json"
    coordinator = build_coordinator(store_path)

    first = coordinator.classify(document)
    second = coordinator.classify(document)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.DUPLICATE
    assert second.version == first.version


def test_changed_document_becomes_new_version(tmp_path: Path) -> None:
    """Changed content creates the next deterministic version."""
    document = tmp_path / "document.txt"
    document.write_text("version one", encoding="utf-8")

    store_path = tmp_path / "metadata" / "identity.json"
    coordinator = build_coordinator(store_path)

    first = coordinator.classify(document)

    document.write_text("version two", encoding="utf-8")

    second = coordinator.classify(document)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.VERSION
    assert second.version == 2


def test_identity_survives_coordinator_recreation(
    tmp_path: Path,
) -> None:
    """Persistent identity survives coordinator recreation."""
    document = tmp_path / "document.txt"
    document.write_text("persistent evidence", encoding="utf-8")

    store_path = tmp_path / "metadata" / "identity.json"

    first_coordinator = build_coordinator(store_path)
    first = first_coordinator.classify(document)

    second_coordinator = build_coordinator(store_path)
    second = second_coordinator.classify(document)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.DUPLICATE
    assert second.version == first.version


def test_get_returns_persisted_identity(tmp_path: Path) -> None:
    """Coordinator exposes the persisted identity decision."""
    document = tmp_path / "document.txt"
    document.write_text("evidence", encoding="utf-8")

    coordinator = build_coordinator(
        tmp_path / "metadata" / "identity.json",
    )

    classified = coordinator.classify(document)
    stored = coordinator.get(document)

    assert stored is not None
    assert stored.content_hash == classified.content_hash
    assert stored.version == classified.version


def test_clear_removes_identity_metadata(tmp_path: Path) -> None:
    """Coordinator can clear persistent identity metadata."""
    document = tmp_path / "document.txt"
    document.write_text("evidence", encoding="utf-8")

    coordinator = build_coordinator(
        tmp_path / "metadata" / "identity.json",
    )

    coordinator.classify(document)
    coordinator.clear()

    assert coordinator.get(document) is None
