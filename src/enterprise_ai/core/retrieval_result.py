"""Retrieval result representation."""

from dataclasses import dataclass

from enterprise_ai.core.retrieval import RetrievalRecord


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """A retrieval record paired with a deterministic relevance score."""

    record: RetrievalRecord
    score: int
