"""Deterministic Reciprocal Rank Fusion."""

from collections.abc import Sequence
from dataclasses import dataclass

from enterprise_ai.core.hybrid import HybridCandidate
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_result import RetrievalResult


@dataclass
class _FusionState:
    """Internal mutable state used during RRF accumulation."""

    record: RetrievalRecord
    lexical_rank: int | None = None
    vector_rank: int | None = None
    lexical_score: float = 0.0
    vector_score: float = 0.0
    fusion_score: float = 0.0


class ReciprocalRankFusion:
    """Fuse independent retrieval rankings deterministically."""

    def __init__(self, constant: int = 60) -> None:
        """Initialize RRF."""
        if constant < 1:
            raise ValueError("constant must be positive")

        self._constant = constant

    def fuse(
        self,
        lexical: Sequence[RetrievalResult],
        vector: Sequence[RetrievalResult],
    ) -> tuple[HybridCandidate, ...]:
        """Fuse lexical and vector result lists."""
        candidates: dict[str, _FusionState] = {}

        for rank, result in enumerate(lexical, start=1):
            record = result.record

            candidate = candidates.setdefault(
                record.evidence_id,
                _FusionState(record=record),
            )

            candidate.lexical_rank = rank
            candidate.lexical_score = result.score
            candidate.fusion_score += 1.0 / (self._constant + rank)

        for rank, result in enumerate(vector, start=1):
            record = result.record

            candidate = candidates.setdefault(
                record.evidence_id,
                _FusionState(record=record),
            )

            candidate.vector_rank = rank
            candidate.vector_score = result.score
            candidate.fusion_score += 1.0 / (self._constant + rank)

        results = tuple(
            HybridCandidate(
                record=value.record,
                lexical_rank=value.lexical_rank,
                vector_rank=value.vector_rank,
                lexical_score=value.lexical_score,
                vector_score=value.vector_score,
                fusion_score=value.fusion_score,
            )
            for value in candidates.values()
        )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -item.fusion_score,
                    item.record.chunk_index,
                    item.record.evidence_id,
                ),
            )
        )
