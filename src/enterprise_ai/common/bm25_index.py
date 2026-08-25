"""Deterministic BM25-style local retrieval."""

import math
import re
from collections import Counter
from collections.abc import Iterable

from enterprise_ai.core.bm25 import BM25Document
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.retrieval_filter import RetrievalFilter
from enterprise_ai.core.retrieval_result import RetrievalResult


class BM25Index:
    """Small deterministic BM25 retrieval index."""

    def __init__(
        self,
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        """Initialize the BM25 index."""
        if k1 < 0:
            raise ValueError("k1 must be non-negative")

        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1")

        self._k1 = k1
        self._b = b
        self._documents: tuple[BM25Document, ...] = ()
        self._document_frequency: dict[str, int] = {}
        self._average_length = 0.0

    def add_many(self, records: Iterable[RetrievalRecord]) -> None:
        """Build deterministic BM25 statistics."""
        documents = tuple(
            BM25Document(
                document_id=record.document_id,
                chunk_id=record.chunk_id,
                evidence_id=record.evidence_id,
                source_path=record.source_path,
                chunk_index=record.chunk_index,
                text=record.text,
                tokens=self._tokenize(record.text),
            )
            for record in records
        )

        self._documents = documents

        frequencies: Counter[str] = Counter()

        for document in documents:
            frequencies.update(set(document.tokens))

        self._document_frequency = dict(frequencies)

        if documents:
            self._average_length = sum(len(document.tokens) for document in documents) / len(
                documents
            )
        else:
            self._average_length = 0.0

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        metadata_filter: RetrievalFilter | None = None,
    ) -> tuple[RetrievalResult, ...]:
        """Return documents ranked by deterministic BM25 score."""
        if limit <= 0:
            return ()

        query_tokens = self._tokenize(query)

        if not query_tokens or not self._documents:
            return ()

        results: list[RetrievalResult] = []
        total_documents = len(self._documents)

        for document in self._documents:
            if metadata_filter is not None and not metadata_filter.matches(
                document_id=document.document_id,
                source_path=document.source_path,
                chunk_id=document.chunk_id,
                chunk_index=document.chunk_index,
            ):
                continue

            term_frequencies = Counter(document.tokens)
            document_length = len(document.tokens)

            if document_length == 0:
                continue

            score = 0.0

            for token in query_tokens:
                term_frequency = term_frequencies.get(token, 0)

                if term_frequency == 0:
                    continue

                document_frequency = self._document_frequency.get(token, 0)

                idf = math.log(
                    1.0 + (total_documents - document_frequency + 0.5) / (document_frequency + 0.5)
                )

                denominator = term_frequency + self._k1 * (
                    1.0 - self._b + self._b * document_length / self._average_length
                )

                score += idf * term_frequency * (self._k1 + 1.0) / denominator

            if score > 0:
                results.append(
                    RetrievalResult(
                        record=RetrievalRecord(
                            evidence_id=document.evidence_id,
                            document_id=document.document_id,
                            chunk_id=document.chunk_id,
                            source_path=document.source_path,
                            chunk_index=document.chunk_index,
                            text=document.text,
                        ),
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
    def _tokenize(text: str) -> tuple[str, ...]:
        """Normalize text into deterministic lowercase tokens."""
        return tuple(re.findall(r"[a-z0-9]+", text.lower()))
