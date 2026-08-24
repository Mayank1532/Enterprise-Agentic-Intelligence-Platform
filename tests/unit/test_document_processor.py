"""Document extraction and chunking tests."""

from pathlib import Path

import pytest

from enterprise_ai.common.document_ingestor import DocumentIngestor
from enterprise_ai.common.document_processor import TextDocumentProcessor
from enterprise_ai.common.file_processor import FileProcessor
from enterprise_ai.common.processing_cache import ProcessingCache


def create_ingestor(tmp_path: Path) -> DocumentIngestor:
    """Create a document ingestor with a temporary cache."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    processor = FileProcessor(
        cache=cache,
        chunk_size=16,
        max_file_size=4096,
    )

    return DocumentIngestor(processor)


def create_document(tmp_path: Path):
    """Create a test document and its provenance record."""
    path = tmp_path / "document.txt"
    path.write_text(
        "Enterprise   Agentic\n\nIntelligence Platform",
        encoding="utf-8",
    )

    ingestor = create_ingestor(tmp_path)

    return path, ingestor.ingest(path)


def test_text_is_extracted(tmp_path: Path) -> None:
    """UTF-8 text must be extracted correctly."""
    path, _ = create_document(tmp_path)

    processor = TextDocumentProcessor(chunk_size=10)

    text = processor.extract(path)

    assert text == "Enterprise   Agentic\n\nIntelligence Platform"


def test_text_is_normalized(tmp_path: Path) -> None:
    """Whitespace normalization must be deterministic."""
    processor = TextDocumentProcessor()

    result = processor.normalize(
        "Enterprise   Agentic\n\nIntelligence   Platform"
    )

    assert result == "Enterprise Agentic Intelligence Platform"


def test_document_is_chunked_with_provenance(tmp_path: Path) -> None:
    """Every chunk must retain its document provenance."""
    _, document = create_document(tmp_path)

    processor = TextDocumentProcessor(chunk_size=10)

    text = processor.extract(Path(document.source_path))
    chunks = processor.chunk(document, text)

    assert len(chunks) > 1

    for index, chunk in enumerate(chunks):
        assert chunk.document_id == document.document_id
        assert chunk.source_path == document.source_path
        assert chunk.chunk_index == index
        assert chunk.text
        assert len(chunk.chunk_id) == 64


def test_same_document_produces_same_chunk_ids(tmp_path: Path) -> None:
    """Identical document content must produce deterministic chunk IDs."""
    _, document = create_document(tmp_path)

    processor = TextDocumentProcessor(chunk_size=10)

    text = processor.extract(Path(document.source_path))

    first = processor.chunk(document, text)
    second = processor.chunk(document, text)

    assert [chunk.chunk_id for chunk in first] == [
        chunk.chunk_id for chunk in second
    ]


def test_empty_document_produces_no_chunks(tmp_path: Path) -> None:
    """An empty document must not create empty chunks."""
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    ingestor = create_ingestor(tmp_path)
    document = ingestor.ingest(path)

    processor = TextDocumentProcessor()

    text = processor.extract(path)
    chunks = processor.chunk(document, text)

    assert chunks == []


def test_invalid_chunk_size_is_rejected() -> None:
    """Invalid chunk sizes must fail explicitly."""
    with pytest.raises(ValueError, match="greater than zero"):
        TextDocumentProcessor(chunk_size=0)
