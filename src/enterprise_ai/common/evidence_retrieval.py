"""Evidence-backed retrieval orchestration."""

from enterprise_ai.common.confidence_calculator import ConfidenceCalculator
from enterprise_ai.common.hybrid_retriever import HybridRetriever
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.evidence_result import (
    EvidenceResult,
    RetrievalResponse,
)
from enterprise_ai.core.reranker import Reranker
from enterprise_ai.core.retrieval_filter import RetrievalFilter


class EvidenceRetrievalService:
    """Retrieve, rerank, score, and cite evidence."""

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        reranker: Reranker,
        confidence_calculator: ConfidenceCalculator | None = None,
    ) -> None:
        """Initialize the evidence retrieval service."""
        self._hybrid_retriever = hybrid_retriever
        self._reranker = reranker
        self._confidence_calculator = confidence_calculator or ConfidenceCalculator()

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        metadata_filter: RetrievalFilter | None = None,
    ) -> RetrievalResponse:
        """Return ranked, confidence-scored, cited evidence."""
        if limit <= 0:
            return RetrievalResponse(
                query=query,
                results=(),
            )

        candidates = self._hybrid_retriever.search(
            query,
            limit=limit,
            metadata_filter=metadata_filter,
        )

        if not candidates:
            return RetrievalResponse(
                query=query,
                results=(),
            )

        records = tuple(candidate.record for candidate in candidates)

        rerank_scores = self._reranker.rerank(
            query,
            records,
        )

        if len(rerank_scores) != len(records):
            raise ValueError("reranker must return one score per candidate")

        ranked = sorted(
            zip(
                candidates,
                rerank_scores,
                strict=True,
            ),
            key=lambda item: (
                -item[1],
                item[0].record.chunk_index,
                item[0].record.evidence_id,
            ),
        )

        results: list[EvidenceResult] = []

        for candidate, rerank_score in ranked[:limit]:
            record = candidate.record

            confidence = self._confidence_calculator.calculate(
                candidate,
                rerank_score,
                candidate_count=len(candidates),
            )

            citation = Citation(
                evidence_id=record.evidence_id,
                document_id=record.document_id,
                chunk_id=record.chunk_id,
                source_path=record.source_path,
                chunk_index=record.chunk_index,
            )

            results.append(
                EvidenceResult(
                    record=record,
                    confidence=confidence,
                    citation=citation,
                    rerank_score=rerank_score,
                )
            )

        return RetrievalResponse(
            query=query,
            results=tuple(results),
        )
