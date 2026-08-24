"""Bounded file processing tests."""

from pathlib import Path

import pytest

from enterprise_ai.common.file_processor import FileProcessor
from enterprise_ai.common.processing_cache import ProcessingCache


def create_processor(tmp_path: Path) -> FileProcessor:
    """Create a processor backed by a temporary cache."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    return FileProcessor(
        cache=cache,
        chunk_size=4,
        max_file_size=1024,
    )


def test_file_is_processed_without_loading_entire_file(
    tmp_path: Path,
) -> None:
    """A file is processed and its metadata is returned."""
    path = tmp_path / "document.txt"
    path.write_bytes(b"enterprise agentic intelligence")

    processor = create_processor(tmp_path)

    result = processor.process(path)

    assert result.size_bytes == path.stat().st_size
    assert len(result.content_hash) == 64
    assert result.reused is False


def test_second_processing_reuses_cached_result(
    tmp_path: Path,
) -> None:
    """The same file content must reuse the cached result."""
    path = tmp_path / "document.txt"
    path.write_bytes(b"same document")

    processor = create_processor(tmp_path)

    first = processor.process(path)
    second = processor.process(path)

    assert first.reused is False
    assert second.reused is True
    assert first.content_hash == second.content_hash


def test_changed_file_content_is_processed_again(
    tmp_path: Path,
) -> None:
    """Changed content must trigger processing again."""
    path = tmp_path / "document.txt"
    path.write_bytes(b"version one")

    processor = create_processor(tmp_path)

    first = processor.process(path)

    path.write_bytes(b"version two")

    second = processor.process(path)

    assert first.reused is False
    assert second.reused is False
    assert first.content_hash != second.content_hash


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    """Missing files must fail explicitly."""
    processor = create_processor(tmp_path)

    with pytest.raises(FileNotFoundError):
        processor.process(tmp_path / "missing.txt")


def test_oversized_file_is_rejected(tmp_path: Path) -> None:
    """Files above the configured limit must be rejected."""
    path = tmp_path / "large.bin"
    path.write_bytes(b"123456789")

    cache = ProcessingCache(str(tmp_path / "cache.db"))

    processor = FileProcessor(
        cache=cache,
        chunk_size=4,
        max_file_size=8,
    )

    with pytest.raises(ValueError, match="maximum size"):
        processor.process(path)
