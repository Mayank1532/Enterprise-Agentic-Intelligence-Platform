"""Deterministic document extraction implementation."""

import re
from pathlib import Path

from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.extraction.models import ExtractedField, ExtractionResult


class DeterministicDocumentExtractor:
    """Extract simple structured fields without an LLM dependency."""

    _email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

    _phone_pattern = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")

    def __init__(self, read_chunk_size: int = 64 * 1024) -> None:
        """Initialize the extractor with a bounded read size."""
        if read_chunk_size <= 0:
            raise ValueError("read_chunk_size must be greater than zero")

        self.read_chunk_size = read_chunk_size

    def extract(self, document: DocumentRecord) -> ExtractionResult:
        """Extract deterministic contact information from the source file."""
        fields: list[ExtractedField] = []

        email_value: str | None = None
        phone_value: str | None = None

        path = Path(document.source_path)

        if not path.is_file():
            return ExtractionResult(
                document_id=document.document_id,
                success=False,
                error=f"Source file not found: {document.source_path}",
            )

        carry = ""

        with path.open("r", encoding="utf-8", errors="replace") as file:
            while True:
                chunk = file.read(self.read_chunk_size)

                if not chunk:
                    break

                text = carry + chunk

                if email_value is None:
                    match = self._email_pattern.search(text)
                    if match:
                        email_value = match.group(0)

                if phone_value is None:
                    match = self._phone_pattern.search(text)
                    if match:
                        phone_value = match.group(0).strip()

                if email_value is not None and phone_value is not None:
                    break

                carry = text[-256:]

        if email_value is not None:
            fields.append(
                ExtractedField(
                    name="email",
                    value=email_value,
                )
            )

        if phone_value is not None:
            fields.append(
                ExtractedField(
                    name="phone",
                    value=phone_value,
                )
            )

        return ExtractionResult(
            document_id=document.document_id,
            fields=tuple(fields),
        )
