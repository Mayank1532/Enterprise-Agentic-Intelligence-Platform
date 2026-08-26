"""Tests for the ADK retrieval tool contract."""

from typing import cast
from unittest.mock import Mock

from enterprise_ai.agents.adk.retrieval_tool import (
    RetrievalTool,
)
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.evidence_result import (
    EvidenceResult,
    RetrievalResponse,
)
from enterprise_ai.core.retrieval import RetrievalRecord
from enterprise_ai.core.tool_result import ToolResult


def make_result() -> EvidenceResult:
    """Create deterministic evidence."""
    record = RetrievalRecord(
        evidence_id="evidence-001",
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=2,
        text="Python retrieval evidence.",
    )

    return EvidenceResult(
        record=record,
        confidence=ConfidenceScore(
            value=0.85,
            basis="deterministic test",
        ),
        citation=Citation(
            evidence_id="evidence-001",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=2,
        ),
        rerank_score=0.85,
    )


def get_result_item(result: ToolResult) -> dict[str, object]:
    """Extract the first result item for assertions."""
    items = result["results"]

    assert isinstance(items, list)
    assert items

    return cast(dict[str, object], items[0])


def test_search_returns_json_safe_contract() -> None:
    """Tool output contains only JSON-safe primitives."""
    service = Mock()
    service.search.return_value = RetrievalResponse(
        query="Python retrieval",
        results=(make_result(),),
    )

    result = RetrievalTool(service).search(
        "Python retrieval",
    )

    assert result == {
        "query": "Python retrieval",
        "results": [
            {
                "evidence_id": "evidence-001",
                "document_id": "document-001",
                "chunk_id": "chunk-001",
                "source_path": "document.txt",
                "chunk_index": 2,
                "text": "Python retrieval evidence.",
                "confidence": 0.85,
            },
        ],
        "has_evidence": True,
    }


def test_search_preserves_provenance() -> None:
    """Tool output preserves Phase 2 provenance."""
    service = Mock()
    service.search.return_value = RetrievalResponse(
        query="Python",
        results=(make_result(),),
    )

    result = RetrievalTool(service).search("Python")

    item = get_result_item(result)

    assert item["evidence_id"] == "evidence-001"
    assert item["document_id"] == "document-001"
    assert item["chunk_id"] == "chunk-001"
    assert item["source_path"] == "document.txt"
    assert item["chunk_index"] == 2


def test_search_preserves_confidence() -> None:
    """Tool output preserves confidence."""
    service = Mock()
    service.search.return_value = RetrievalResponse(
        query="Python",
        results=(make_result(),),
    )

    result = RetrievalTool(service).search("Python")

    item = get_result_item(result)

    assert item["confidence"] == 0.85


def test_empty_query_abstains() -> None:
    """Empty queries return an explicit no-evidence response."""
    service = Mock()

    result = RetrievalTool(service).search("   ")

    assert result == {
        "query": "   ",
        "results": [],
        "has_evidence": False,
    }

    service.search.assert_not_called()


def test_search_delegates_query_and_limit() -> None:
    """Tool delegates retrieval without altering inputs."""
    service = Mock()
    service.search.return_value = RetrievalResponse(
        query="Python",
        results=(),
    )

    RetrievalTool(service).search(
        "Python",
        limit=3,
    )

    service.search.assert_called_once_with(
        "Python",
        limit=3,
    )
