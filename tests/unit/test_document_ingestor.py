"""Document ingestion tests."""

from pathlib import Path

from enterprise_ai.common.document_ingestor import DocumentIngestor
from enterprise_ai.common.file_processor import FileProcessor
from enterprise_ai.common.processing_cache import ProcessingCache


def create_ingestor(tmp_path: Path) -> DocumentIngestor:
    """Create a document ingestor with a temporary cache."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    processor = FileProcessor(
        cache=cache,
        chunk_size=4,
        max_file_size=1024,
    )

    return DocumentIngestor(processor)


def test_document_ingestion_creates_provenance_record(
    tmp_path: Path,
) -> None:
    """Ingestion must produce canonical provenance metadata."""
    path = tmp_path / "policy.txt"
    path.write_text("enterprise policy", encoding="utf-8")

    ingestor = create_ingestor(tmp_path)

    record = ingestor.ingest(path)

    assert record.document_id == record.content_hash
    assert record.source_path == str(path.resolve())
    assert record.size_bytes == path.stat().st_size
    assert record.suffix == ".txt"
    assert record.reused is False


def test_repeated_document_ingestion_reuses_processing(
    tmp_path: Path,
) -> None:
    """Repeated ingestion of unchanged content must reuse processing."""
    path = tmp_path / "policy.txt"
    path.write_text("same policy", encoding="utf-8")

    ingestor = create_ingestor(tmp_path)

    first = ingestor.ingest(path)
    second = ingestor.ingest(path)

    assert first.document_id == second.document_id
    assert first.content_hash == second.content_hash
    assert first.reused is False
    assert second.reused is True


def test_changed_document_gets_new_identity(
    tmp_path: Path,
) -> None:
    """Changed content must receive a new document identity."""
    path = tmp_path / "policy.txt"
    path.write_text("policy version one", encoding="utf-8")

    ingestor = create_ingestor(tmp_path)

    first = ingestor.ingest(path)

    path.write_text("policy version two", encoding="utf-8")

    second = ingestor.ingest(path)

    assert first.document_id != second.document_id
    assert first.content_hash != second.content_hash
    assert second.reused is False
