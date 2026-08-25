"""Provider-neutral reranking contract."""

from collections.abc import Sequence
from typing import Protocol

from enterprise_ai.core.retrieval import RetrievalRecord


class Reranker(Protocol):
    """Provider-neutral reranking interface."""

    def rerank(
        self,
        query: str,
        records: Sequence[RetrievalRecord],
    ) -> tuple[float, ...]:
        """Return one relevance score for every candidate."""
        ...
