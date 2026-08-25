"""Deterministic local vector retrieval."""

import math
from collections.abc import Iterable

from enterprise_ai.core.embedding import EmbeddingProvider
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_filter import RetrievalFilter
from enterprise_ai.core.retrieval_result import RetrievalResult
from enterprise_ai.core.vector import VectorRecord


class LocalVectorIndex:
    """Small in-memory cosine-similarity vector index."""

    def __init__(self, provider: EmbeddingProvider) -> None:
        """Initialize the vector index."""
        self._provider = provider
        self._records: tuple[VectorRecord, ...] = ()

    def add_many(self, records: Iterable[RetrievalRecord]) -> None:
        """Embed and store retrieval records."""
        retrieval_records = tuple(records)

        self._records = tuple(
            VectorRecord(
                record=record,
                vector=self._provider.embed(record.text),
            )
            for record in retrieval_records
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        metadata_filter: RetrievalFilter | None = None,
    ) -> tuple[RetrievalResult, ...]:
        """Return records ranked by cosine similarity."""
        if limit <= 0:
            return ()

        query_vector = self._provider.embed(query)

        if not any(query_vector):
            return ()

        results: list[RetrievalResult] = []

        for vector_record in self._records:
            record = vector_record.record

            if metadata_filter is not None and not metadata_filter.matches(
                document_id=record.document_id,
                source_path=record.source_path,
                chunk_id=record.chunk_id,
                chunk_index=record.chunk_index,
            ):
                continue

            score = self._cosine_similarity(
                query_vector,
                vector_record.vector,
            )

            if score > 0:
                results.append(
                    RetrievalResult(
                        record=record,
                        score=score,
                    )
                )

        results.sort(
            key=lambda item: (
                -item.score,
                item.record.chunk_index,
                item.record.evidence_id,
            )
        )

        return tuple(results[:limit])

    @staticmethod
    def _cosine_similarity(
        left: tuple[float, ...],
        right: tuple[float, ...],
    ) -> float:
        """Calculate cosine similarity."""
        if len(left) != len(right):
            raise ValueError("vector dimensions must match")

        left_norm = math.sqrt(sum(value * value for value in left))

        right_norm = math.sqrt(sum(value * value for value in right))

        if left_norm == 0 or right_norm == 0:
            return 0.0

        dot_product = sum(
            left_value * right_value
            for left_value, right_value in zip(
                left,
                right,
                strict=True,
            )
        )

        return dot_product / (left_norm * right_norm)
