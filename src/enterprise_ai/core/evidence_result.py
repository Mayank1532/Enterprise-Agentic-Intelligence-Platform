"""Evidence-backed retrieval response."""

from dataclasses import dataclass

from enterprise_ai.core.citation import Citation
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.retrieval import RetrievalRecord


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    """A retrieved record with confidence and provenance."""

    record: RetrievalRecord
    confidence: ConfidenceScore
    citation: Citation
    rerank_score: float

    def __post_init__(self) -> None:
        """Validate reranking score."""
        if self.rerank_score < 0.0:
            raise ValueError("rerank_score must be non-negative")


@dataclass(frozen=True, slots=True)
class RetrievalResponse:
    """Complete evidence-backed retrieval response."""

    query: str
    results: tuple[EvidenceResult, ...]

    @property
    def has_evidence(self) -> bool:
        """Return whether retrieval produced usable evidence."""
        return bool(self.results)
