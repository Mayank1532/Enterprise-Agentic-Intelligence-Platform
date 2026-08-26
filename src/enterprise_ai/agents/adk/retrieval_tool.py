"""Google ADK tool adapter for Phase 2 retrieval."""

from enterprise_ai.common.evidence_retrieval import (
    EvidenceRetrievalService,
)
from enterprise_ai.core.tool_result import (
    RetrievalToolResponse,
    ToolEvidence,
    ToolResult,
)


class RetrievalTool:
    """Expose deterministic evidence retrieval as an ADK tool."""

    def __init__(
        self,
        service: EvidenceRetrievalService,
    ) -> None:
        """Initialize the retrieval tool."""
        self._service = service

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> ToolResult:
        """Search evidence and return a JSON-safe result."""
        if not query.strip():
            return {
                "query": query,
                "results": [],
                "has_evidence": False,
            }

        response = self._service.search(
            query,
            limit=limit,
        )

        result = RetrievalToolResponse(
            query=response.query,
            results=tuple(
                ToolEvidence(
                    evidence_id=item.record.evidence_id,
                    document_id=item.record.document_id,
                    chunk_id=item.record.chunk_id,
                    source_path=item.record.source_path,
                    chunk_index=item.record.chunk_index,
                    text=item.record.text,
                    confidence=item.confidence.value,
                )
                for item in response.results
            ),
            has_evidence=response.has_evidence,
        )

        return {
            "query": result.query,
            "results": [
                {
                    "evidence_id": item.evidence_id,
                    "document_id": item.document_id,
                    "chunk_id": item.chunk_id,
                    "source_path": item.source_path,
                    "chunk_index": item.chunk_index,
                    "text": item.text,
                    "confidence": item.confidence,
                }
                for item in result.results
            ],
            "has_evidence": result.has_evidence,
        }


def create_retrieval_tool(
    service: EvidenceRetrievalService,
) -> RetrievalTool:
    """Create the ADK retrieval tool adapter."""
    return RetrievalTool(service)
