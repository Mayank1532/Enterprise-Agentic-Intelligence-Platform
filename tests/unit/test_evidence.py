"""Tests for deterministic evidence representation."""

from enterprise_ai.common.evidence_builder import EvidenceBuilder
from enterprise_ai.core.chunk import DocumentChunk
from enterprise_ai.core.document import DocumentRecord
from enterprise_ai.core.evidence import EvidenceBlock


def create_inputs() -> tuple[DocumentRecord, DocumentChunk]:
    """Create deterministic document and chunk inputs."""
    document = DocumentRecord(
        document_id="document-001",
        source_path="evidence.txt",
        content_hash="content-hash-001",
        size_bytes=45,
        suffix=".txt",
        reused=False,
    )

    chunk = DocumentChunk(
        chunk_id="chunk-001",
        document_id=document.document_id,
        source_path=document.source_path,
        chunk_index=0,
        text="Enterprise evidence must remain traceable.",
    )

    return document, chunk


def test_build_evidence_block() -> None:
    """Evidence contains document and chunk provenance."""
    document, chunk = create_inputs()

    evidence = EvidenceBuilder.build(document, chunk)

    assert isinstance(evidence, EvidenceBlock)
    assert evidence.document_id == document.document_id
    assert evidence.chunk_id == chunk.chunk_id
    assert evidence.source_path == document.source_path
    assert evidence.chunk_index == chunk.chunk_index
    assert evidence.text == chunk.text


def test_evidence_reference_is_stable() -> None:
    """Evidence reference is derived from stable identifiers."""
    document, chunk = create_inputs()

    evidence = EvidenceBuilder.build(document, chunk)

    assert evidence.reference() == (f"{document.document_id}#{chunk.chunk_id}")


def test_evidence_id_is_deterministic() -> None:
    """Identical input produces an identical evidence ID."""
    document, chunk = create_inputs()

    first = EvidenceBuilder.build(document, chunk)
    second = EvidenceBuilder.build(document, chunk)

    assert first.evidence_id == second.evidence_id


def test_evidence_id_changes_when_chunk_changes() -> None:
    """Different evidence text produces a different evidence ID."""
    document, chunk = create_inputs()

    first = EvidenceBuilder.build(document, chunk)

    changed_chunk = DocumentChunk(
        chunk_id="chunk-002",
        document_id=document.document_id,
        source_path=document.source_path,
        chunk_index=0,
        text="Different evidence.",
    )

    second = EvidenceBuilder.build(document, changed_chunk)

    assert first.evidence_id != second.evidence_id
