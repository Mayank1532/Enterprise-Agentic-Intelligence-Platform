"""Deterministic baseline reranker."""

import re
from collections.abc import Sequence

from enterprise_ai.core.retrieval import RetrievalRecord


class DeterministicReranker:
    """Simple deterministic query-term reranker."""

    def rerank(
        self,
        query: str,
        records: Sequence[RetrievalRecord],
    ) -> tuple[float, ...]:
        """Score candidates by query-token coverage."""
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return tuple(0.0 for _ in records)

        scores: list[float] = []

        for record in records:
            document_tokens = self._tokenize(record.text)

            if not document_tokens:
                scores.append(0.0)
                continue

            matched = sum(1 for token in query_tokens if token in document_tokens)

            scores.append(matched / len(query_tokens))

        return tuple(scores)

    @staticmethod
    def _tokenize(text: str) -> frozenset[str]:
        """Normalize text into deterministic lowercase tokens."""
        return frozenset(
            re.findall(
                r"[a-z0-9]+",
                text.lower(),
            )
        )
