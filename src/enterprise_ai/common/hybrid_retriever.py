"""Hybrid retrieval orchestration."""

from enterprise_ai.common.bm25_index import BM25Index
from enterprise_ai.common.local_vector_index import LocalVectorIndex
from enterprise_ai.common.rrf import ReciprocalRankFusion
from enterprise_ai.core.hybrid import HybridCandidate
from enterprise_ai.core.retrieval_filter import RetrievalFilter


class HybridRetriever:
    """Combine lexical and vector retrieval."""

    def __init__(
        self,
        lexical: BM25Index,
        vector: LocalVectorIndex,
        fusion: ReciprocalRankFusion | None = None,
    ) -> None:
        """Initialize the hybrid retriever."""
        self._lexical = lexical
        self._vector = vector
        self._fusion = fusion or ReciprocalRankFusion()

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        metadata_filter: RetrievalFilter | None = None,
    ) -> tuple[HybridCandidate, ...]:
        """Return candidates fused from both retrieval systems."""
        if limit <= 0:
            return ()

        lexical_results = self._lexical.search(
            query,
            limit=limit,
            metadata_filter=metadata_filter,
        )

        vector_results = self._vector.search(
            query,
            limit=limit,
            metadata_filter=metadata_filter,
        )

        fused = self._fusion.fuse(
            lexical_results,
            vector_results,
        )

        return fused[:limit]
