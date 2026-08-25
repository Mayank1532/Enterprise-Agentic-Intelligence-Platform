"""Document extraction interfaces."""

from typing import Protocol

from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.extraction.models import ExtractionResult


class DocumentExtractor(Protocol):
    """Protocol for provider-neutral document extractors."""

    def extract(self, document: DocumentRecord) -> ExtractionResult:
        """Extract structured information from a document."""
        ...
