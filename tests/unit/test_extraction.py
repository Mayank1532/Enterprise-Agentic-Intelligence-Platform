"""Tests for structured document extraction."""

from pathlib import Path

from enterprise_ai.common.document_ingestor import DocumentIngestor
from enterprise_ai.common.file_processor import FileProcessor
from enterprise_ai.common.processing_cache import ProcessingCache
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.extraction.deterministic import DeterministicDocumentExtractor


def test_extracts_email(tmp_path: Path) -> None:
    """Email addresses are extracted deterministically."""
    document = create_document(
        tmp_path,
        "Contact us at analyst@example.com for details.",
    )

    result = DeterministicDocumentExtractor().extract(document)

    assert result.success is True
    assert result.document_id == document.document_id
    assert result.field_count == 1
    assert result.fields[0].name == "email"
    assert result.fields[0].value == "analyst@example.com"


def test_extracts_phone(tmp_path: Path) -> None:
    """Phone numbers are extracted deterministically."""
    document = create_document(
        tmp_path,
        "Call +1 555-123-4567 for support.",
    )

    result = DeterministicDocumentExtractor().extract(document)

    assert result.success is True
    assert result.field_count == 1
    assert result.fields[0].name == "phone"


def test_extracts_multiple_fields(tmp_path: Path) -> None:
    """Multiple supported fields are returned."""
    document = create_document(
        tmp_path,
        "Email: analyst@example.com. Phone: +1 555-123-4567.",
    )

    result = DeterministicDocumentExtractor().extract(document)

    assert result.success is True
    assert result.field_count == 2
    assert {field.name for field in result.fields} == {"email", "phone"}


def test_returns_empty_result_when_no_fields_found(tmp_path: Path) -> None:
    """Documents without supported fields return an empty result."""
    document = create_document(
        tmp_path,
        "This document contains no contact information.",
    )

    result = DeterministicDocumentExtractor().extract(document)

    assert result.success is True
    assert result.field_count == 0
    assert result.error is None


def test_extraction_is_repeatable(tmp_path: Path) -> None:
    """The same input produces the same extraction result."""
    document = create_document(
        tmp_path,
        "Contact analyst@example.com.",
    )

    extractor = DeterministicDocumentExtractor()

    first = extractor.extract(document)
    second = extractor.extract(document)

    assert first == second


def create_document(tmp_path: Path, content: str) -> DocumentRecord:
    """Create a real DocumentRecord using the existing ingestion contract."""
    path = tmp_path / "sample.txt"
    path.write_text(content, encoding="utf-8")

    cache = ProcessingCache()
    file_processor = FileProcessor(cache)
    ingestor = DocumentIngestor(file_processor)

    return ingestor.ingest(path)
