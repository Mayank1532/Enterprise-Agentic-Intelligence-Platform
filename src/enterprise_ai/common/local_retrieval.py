"""Deterministic local lexical retrieval."""

import re
from collections.abc import Iterable

from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_result import RetrievalResult


class LocalRetrievalIndex:
    """Small deterministic lexical retrieval index."""

    def __init__(self) -> None:
        """Initialize an empty retrieval index."""
        self._records: tuple[RetrievalRecord, ...] = ()

    def add_many(self, records: Iterable[RetrievalRecord]) -> None:
        """Replace the index contents with deterministic records."""
        self._records = tuple(records)

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[RetrievalResult, ...]:
        """Return records ranked by deterministic token overlap."""
        if limit <= 0:
            return ()

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return ()

        results: list[RetrievalResult] = []

        for record in self._records:
            document_tokens = self._tokenize(record.text)
            score = sum(
                1
                for token in query_tokens
                if token in document_tokens
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
    def _tokenize(text: str) -> frozenset[str]:
        """Normalize text into deterministic lowercase tokens."""
        return frozenset(
            re.findall(r"[a-z0-9]+", text.lower())
        )
