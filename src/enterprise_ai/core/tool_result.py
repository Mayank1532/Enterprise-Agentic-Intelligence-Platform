"""ADK tool result representation."""

from dataclasses import dataclass
from typing import TypeAlias


JSONPrimitive: TypeAlias = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class ToolEvidence:
    """Evidence exposed through an ADK tool."""

    evidence_id: str
    document_id: str
    chunk_id: str
    source_path: str
    chunk_index: int
    text: str
    confidence: float


@dataclass(frozen=True, slots=True)
class RetrievalToolResponse:
    """Stable response returned by the retrieval tool."""

    query: str
    results: tuple[ToolEvidence, ...]
    has_evidence: bool


ToolResult: TypeAlias = dict[
    str,
    JSONPrimitive | list[dict[str, JSONPrimitive]],
]
