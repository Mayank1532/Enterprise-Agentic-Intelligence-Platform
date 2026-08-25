"""Tests for deterministic document identity registry."""

from pathlib import Path

from enterprise_ai.identity.registry import (
    DocumentIdentityRegistry,
    IdentityStatus,
)


def test_first_document_is_new(tmp_path: Path) -> None:
    """The first occurrence of a document is classified as new."""
    path = tmp_path / "document.txt"
    path.write_text("enterprise evidence", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    decision = registry.register(path)

    assert decision.status == IdentityStatus.NEW
    assert decision.version == 1
    assert decision.content_hash


def test_same_path_same_content_is_duplicate(tmp_path: Path) -> None:
    """Re-registering unchanged content is classified as duplicate."""
    path = tmp_path / "document.txt"
    path.write_text("enterprise evidence", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    first = registry.register(path)
    second = registry.register(path)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.DUPLICATE
    assert second.version == 1
    assert second.content_hash == first.content_hash


def test_changed_same_path_creates_new_version(tmp_path: Path) -> None:
    """Changed content at the same source path creates a new version."""
    path = tmp_path / "document.txt"
    path.write_text("version one", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    first = registry.register(path)

    path.write_text("version two", encoding="utf-8")

    second = registry.register(path)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.VERSION
    assert second.version == 2
    assert second.content_hash != first.content_hash


def test_identical_content_at_different_paths_is_duplicate(
    tmp_path: Path,
) -> None:
    """Identical content at different paths is a duplicate."""
    first_path = tmp_path / "first.txt"
    second_path = tmp_path / "second.txt"

    first_path.write_text("same evidence", encoding="utf-8")
    second_path.write_text("same evidence", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    first = registry.register(first_path)
    second = registry.register(second_path)

    assert first.status == IdentityStatus.NEW
    assert second.status == IdentityStatus.DUPLICATE
    assert second.version == 1
    assert second.content_hash == first.content_hash


def test_get_returns_registered_identity(tmp_path: Path) -> None:
    """Registered identity can be retrieved by source path."""
    path = tmp_path / "document.txt"
    path.write_text("evidence", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    registered = registry.register(path)
    retrieved = registry.get(path)

    assert retrieved == registered


def test_get_unknown_document_returns_none(tmp_path: Path) -> None:
    """Unknown documents return no identity."""
    path = tmp_path / "unknown.txt"

    registry = DocumentIdentityRegistry()

    assert registry.get(path) is None


def test_clear_removes_registered_identities(tmp_path: Path) -> None:
    """Clear removes all registered identities."""
    path = tmp_path / "document.txt"
    path.write_text("evidence", encoding="utf-8")

    registry = DocumentIdentityRegistry()

    registry.register(path)
    registry.clear()

    assert registry.get(path) is None
