"""Structured document extraction domain models."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExtractedField:
    """A single extracted field with source evidence."""

    name: str
    value: str
    source_chunk_id: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class ExtractionResult:
    """Provider-neutral structured extraction result."""

    document_id: str
    fields: tuple[ExtractedField, ...] = field(default_factory=tuple)
    success: bool = True
    error: str | None = None

    @property
    def field_count(self) -> int:
        """Return the number of extracted fields."""
        return len(self.fields)
