"""Document ingestion service."""

from pathlib import Path

from enterprise_ai.common.file_processor import FileProcessor, ProcessingResult
from enterprise_ai.core.document import DocumentRecord


class DocumentIngestor:
    """Ingest documents using bounded processing and cached results."""

    def __init__(self, processor: FileProcessor) -> None:
        self.processor = processor

    def ingest(self, path: Path) -> DocumentRecord:
        """Ingest a document and return its provenance metadata."""
        result: ProcessingResult = self.processor.process(path)

        return DocumentRecord(
            document_id=result.content_hash,
            source_path=str(path.resolve()),
            content_hash=result.content_hash,
            size_bytes=result.size_bytes,
            suffix=path.suffix.lower(),
            reused=result.reused,
        )
