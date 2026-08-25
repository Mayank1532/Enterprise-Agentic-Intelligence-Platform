"""Tests for deterministic citations."""

import pytest

from enterprise_ai.core.citation import Citation


def test_citation_preserves_provenance() -> None:
    """Citation preserves all retrieval provenance."""
    citation = Citation(
        evidence_id="evidence-001",
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=3,
    )

    assert citation.evidence_id == "evidence-001"
    assert citation.document_id == "document-001"
    assert citation.chunk_id == "chunk-001"
    assert citation.source_path == "document.txt"
    assert citation.chunk_index == 3


def test_empty_identity_fails() -> None:
    """Empty citation identity is rejected."""
    with pytest.raises(ValueError):
        Citation(
            evidence_id="",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=0,
        )


def test_negative_chunk_index_fails() -> None:
    """Negative chunk indexes are rejected."""
    with pytest.raises(ValueError):
        Citation(
            evidence_id="evidence-001",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=-1,
        )
