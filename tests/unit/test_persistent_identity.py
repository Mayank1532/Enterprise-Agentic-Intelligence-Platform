"""Tests for persistent document identity metadata."""

from pathlib import Path

from enterprise_ai.identity.persistent_registry import (
    PersistentDocumentIdentityRegistry,
)
from enterprise_ai.identity.registry import IdentityStatus
from enterprise_ai.identity.store import IdentityStore


def test_store_missing_file_returns_empty(tmp_path: Path) -> None:
    """A missing store starts empty."""
    store = IdentityStore(tmp_path / "identity.json")

    assert store.load() == {}


def test_identity_survives_registry_recreation(tmp_path: Path) -> None:
    """Identity metadata survives a new registry instance."""
    document = tmp_path / "document.txt"
    store_path = tmp_path / "metadata" / "identity.json"

    document.write_text("persistent evidence", encoding="utf-8")

    first_registry = PersistentDocumentIdentityRegistry(store_path)
    first = first_registry.register(document)

    second_registry = PersistentDocumentIdentityRegistry(store_path)
    second = second_registry.register(document)

    assert first.status == IdentityStatus.NEW
    assert first.version == 1
    assert second.status == IdentityStatus.DUPLICATE
    assert second.version == 1
    assert second.content_hash == first.content_hash


def test_changed_document_increments_persisted_version(
    tmp_path: Path,
) -> None:
    """Changed content increments version after registry recreation."""
    document = tmp_path / "document.txt"
    store_path = tmp_path / "metadata" / "identity.json"

    document.write_text("version one", encoding="utf-8")

    first_registry = PersistentDocumentIdentityRegistry(store_path)
    first = first_registry.register(document)

    document.write_text("version two", encoding="utf-8")

    second_registry = PersistentDocumentIdentityRegistry(store_path)
    second = second_registry.register(document)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.VERSION
    assert second.version == 2
    assert second.content_hash != first.content_hash


def test_store_is_created_and_contains_identity(
    tmp_path: Path,
) -> None:
    """Registration creates readable persistent metadata."""
    document = tmp_path / "document.txt"
    store_path = tmp_path / "metadata" / "identity.json"

    document.write_text("stored evidence", encoding="utf-8")

    registry = PersistentDocumentIdentityRegistry(store_path)
    registry.register(document)

    assert store_path.exists()

    store = IdentityStore(store_path)
    loaded = store.load()

    assert str(document.resolve()) in loaded
    assert loaded[str(document.resolve())].version == 1


def test_clear_removes_persistent_metadata(tmp_path: Path) -> None:
    """Clear removes persisted metadata."""
    document = tmp_path / "document.txt"
    store_path = tmp_path / "metadata" / "identity.json"

    document.write_text("evidence", encoding="utf-8")

    registry = PersistentDocumentIdentityRegistry(store_path)
    registry.register(document)

    registry.clear()

    assert not store_path.exists()
    assert registry.get(document) is None
