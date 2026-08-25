"""Vector retrieval representation."""

from dataclasses import dataclass

from enterprise_ai.core.retrieval import RetrievalRecord


@dataclass(frozen=True, slots=True)
class VectorRecord:
    """A retrieval record paired with an embedding vector."""

    record: RetrievalRecord
    vector: tuple[float, ...]
