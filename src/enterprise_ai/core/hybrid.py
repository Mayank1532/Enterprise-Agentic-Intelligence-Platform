"""Hybrid retrieval representation."""

from dataclasses import dataclass

from enterprise_ai.core.retrieval import RetrievalRecord


@dataclass(frozen=True, slots=True)
class HybridCandidate:
    """A candidate produced by multiple retrieval strategies."""

    record: RetrievalRecord
    lexical_rank: int | None
    vector_rank: int | None
    lexical_score: float
    vector_score: float
    fusion_score: float
