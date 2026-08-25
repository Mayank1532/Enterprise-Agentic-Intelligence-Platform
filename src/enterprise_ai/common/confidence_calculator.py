"""Deterministic confidence calculation."""

from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.hybrid import HybridCandidate


class ConfidenceCalculator:
    """Convert retrieval and reranking signals into bounded confidence."""

    def calculate(
        self,
        candidate: HybridCandidate,
        rerank_score: float,
        *,
        candidate_count: int,
    ) -> ConfidenceScore:
        """Calculate deterministic bounded confidence."""
        if candidate_count < 1:
            raise ValueError("candidate_count must be positive")

        if rerank_score < 0.0:
            raise ValueError("rerank_score must be non-negative")

        agreement = self._agreement(candidate)

        rank_signal = 1.0 / max(
            candidate.lexical_rank or candidate.vector_rank or 1,
            1,
        )

        normalized_fusion = min(
            candidate.fusion_score * 60.0,
            1.0,
        )

        normalized_rerank = min(
            rerank_score,
            1.0,
        )

        candidate_signal = 1.0 / candidate_count

        confidence = (
            0.40 * normalized_rerank
            + 0.25 * normalized_fusion
            + 0.20 * agreement
            + 0.10 * rank_signal
            + 0.05 * candidate_signal
        )

        return ConfidenceScore(
            value=max(0.0, min(confidence, 1.0)),
            basis=(
                "deterministic hybrid fusion, rerank score, "
                "retriever agreement, rank, and candidate count"
            ),
        )

    @staticmethod
    def _agreement(candidate: HybridCandidate) -> float:
        """Return agreement between lexical and vector retrieval."""
        if candidate.lexical_rank is not None and candidate.vector_rank is not None:
            return 1.0

        return 0.0
