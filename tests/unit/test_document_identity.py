"""Tests for deterministic document identity."""

from pathlib import Path

import pytest

from enterprise_ai.identity.service import (
    DocumentIdentityService,
)


def test_same_content_produces_same_hash(tmp_path: Path) -> None:
    """Identical content produces an identical hash."""
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("enterprise evidence", encoding="utf-8")
    second.write_text("enterprise evidence", encoding="utf-8")

    service = DocumentIdentityService()

    assert service.content_hash(first) == service.content_hash(second)


def test_different_content_produces_different_hash(tmp_path: Path) -> None:
    """Different content produces different hashes."""
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("version one", encoding="utf-8")
    second.write_text("version two", encoding="utf-8")

    service = DocumentIdentityService()

    assert service.content_hash(first) != service.content_hash(second)


def test_identity_contains_file_size_and_version(tmp_path: Path) -> None:
    """Identity contains deterministic size and explicit version."""
    path = tmp_path / "document.txt"
    content = "document content"

    path.write_text(content, encoding="utf-8")

    service = DocumentIdentityService()
    identity = service.identify(path, version=3)

    assert identity.content_hash
    assert identity.size_bytes == path.stat().st_size
    assert identity.version == 3


def test_same_content_detection(tmp_path: Path) -> None:
    """Duplicate files are detected by content."""
    first = tmp_path / "first.txt"
    second = tmp_path / "duplicate.txt"

    first.write_text("same evidence", encoding="utf-8")
    second.write_text("same evidence", encoding="utf-8")

    service = DocumentIdentityService()

    assert service.is_same_content(first, second) is True


def test_changed_content_detection(tmp_path: Path) -> None:
    """Changed files are detected by content."""
    first = tmp_path / "first.txt"
    second = tmp_path / "changed.txt"

    first.write_text("original evidence", encoding="utf-8")
    second.write_text("changed evidence", encoding="utf-8")

    service = DocumentIdentityService()

    assert service.is_same_content(first, second) is False


def test_missing_file_fails_clearly(tmp_path: Path) -> None:
    """Missing files produce an explicit error."""
    path = tmp_path / "missing.txt"

    service = DocumentIdentityService()

    with pytest.raises(FileNotFoundError):
        service.content_hash(path)


def test_invalid_chunk_size_is_rejected() -> None:
    """Invalid read sizes are rejected."""
    with pytest.raises(ValueError):
        DocumentIdentityService(read_chunk_size=0)


def test_invalid_version_is_rejected(tmp_path: Path) -> None:
    """Invalid document versions are rejected."""
    path = tmp_path / "document.txt"
    path.write_text("content", encoding="utf-8")

    service = DocumentIdentityService()

    with pytest.raises(ValueError):
        service.identify(path, version=0)
