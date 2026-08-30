"""Tests for Phase 7 grounding integration with existing citations."""

import pytest

from enterprise_ai.common.grounding_verifier import GroundingVerifier
from enterprise_ai.core.citation import Citation
from enterprise_ai.core.claim import Claim
from enterprise_ai.core.claim_support import ClaimSupport
from enterprise_ai.core.confidence import ConfidenceScore
from enterprise_ai.core.evidence_result import EvidenceResult
from enterprise_ai.core.grounding_policy import GroundingPolicy
from enterprise_ai.core.retrieval import RetrievalRecord


def make_record(
    evidence_id: str = "evidence-001",
) -> RetrievalRecord:
    """Create deterministic retrieval evidence."""
    return RetrievalRecord(
        evidence_id=evidence_id,
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=0,
        text="Python retrieval evidence.",
    )


def make_citation(
    evidence_id: str = "evidence-001",
    document_id: str = "document-001",
    chunk_id: str = "chunk-001",
    source_path: str = "document.txt",
    chunk_index: int = 0,
) -> Citation:
    """Create deterministic provenance."""
    return Citation(
        evidence_id=evidence_id,
        document_id=document_id,
        chunk_id=chunk_id,
        source_path=source_path,
        chunk_index=chunk_index,
    )


def make_evidence_result(
    *,
    evidence_id: str = "evidence-001",
    citation: Citation | None = None,
    confidence: float = 0.90,
) -> EvidenceResult:
    """Create a complete evidence result."""
    record = make_record(evidence_id)

    return EvidenceResult(
        record=record,
        confidence=ConfidenceScore(
            value=confidence,
            basis="deterministic test",
        ),
        citation=citation or make_citation(evidence_id=evidence_id),
        rerank_score=confidence,
    )


def make_claim() -> Claim:
    """Create a deterministic claim."""
    return Claim(
        claim_id="claim-001",
        text="Python retrieval is supported by the evidence.",
    )


# ============================================================
# Citation ↔ EvidenceResult consistency
# ============================================================


def test_valid_evidence_result_has_consistent_citation() -> None:
    """Citation provenance matches its evidence record."""
    result = make_evidence_result()

    assert result.citation.evidence_id == result.record.evidence_id
    assert result.citation.document_id == result.record.document_id
    assert result.citation.chunk_id == result.record.chunk_id
    assert result.citation.source_path == result.record.source_path
    assert result.citation.chunk_index == result.record.chunk_index


def test_mismatched_citation_evidence_id_is_detectable() -> None:
    """A citation pointing to another evidence ID must be rejected."""
    result = make_evidence_result(
        citation=make_citation(
            evidence_id="different-evidence",
        ),
    )

    assert result.citation.evidence_id != result.record.evidence_id


def test_mismatched_citation_document_id_is_detectable() -> None:
    """A citation pointing to another document must be rejected."""
    result = make_evidence_result(
        citation=make_citation(
            document_id="different-document",
        ),
    )

    assert result.citation.document_id != result.record.document_id


def test_mismatched_citation_chunk_id_is_detectable() -> None:
    """A citation pointing to another chunk must be rejected."""
    result = make_evidence_result(
        citation=make_citation(
            chunk_id="different-chunk",
        ),
    )

    assert result.citation.chunk_id != result.record.chunk_id


def test_mismatched_citation_source_is_detectable() -> None:
    """A citation pointing to another source must be rejected."""
    result = make_evidence_result(
        citation=make_citation(
            source_path="different.txt",
        ),
    )

    assert result.citation.source_path != result.record.source_path


def test_mismatched_citation_chunk_index_is_detectable() -> None:
    """A citation pointing to another chunk position must be rejected."""
    result = make_evidence_result(
        citation=make_citation(
            chunk_index=5,
        ),
    )

    assert result.citation.chunk_index != result.record.chunk_index


# ============================================================
# Citation availability
# ============================================================


def test_valid_citation_references_available_evidence() -> None:
    """A valid citation can be resolved against available evidence."""
    result = make_evidence_result()

    available_evidence = {
        result.record.evidence_id,
    }

    assert result.citation.evidence_id in available_evidence


def test_missing_citation_evidence_is_detectable() -> None:
    """A citation must reference evidence actually supplied."""
    result = make_evidence_result(
        evidence_id="evidence-001",
    )

    available_evidence = {
        "evidence-999",
    }

    assert result.citation.evidence_id not in available_evidence


# ============================================================
# Grounding integration behavior
# ============================================================


def test_valid_evidence_can_support_grounded_claim() -> None:
    """Valid evidence and support should produce grounding."""
    result = make_evidence_result()

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    support = ClaimSupport(
        claim_id="claim-001",
        evidence_ids=(result.citation.evidence_id,),
        supported=True,
        confidence=result.confidence.value,
    )

    grounding = verifier.verify(
        claims=(make_claim(),),
        supports=(support,),
        evidence_ids={
            result.record.evidence_id,
        },
    )

    assert grounding.grounded is True
    assert grounding.abstain is False


def test_missing_cited_evidence_causes_abstention() -> None:
    """A citation referring to unavailable evidence cannot ground a claim."""
    result = make_evidence_result()

    verifier = GroundingVerifier()

    support = ClaimSupport(
        claim_id="claim-001",
        evidence_ids=(result.citation.evidence_id,),
        supported=True,
        confidence=0.95,
    )

    grounding = verifier.verify(
        claims=(make_claim(),),
        supports=(support,),
        evidence_ids={"different-evidence"},
    )

    assert grounding.grounded is False
    assert grounding.abstain is True
    assert grounding.reasons


def test_low_confidence_evidence_does_not_ground_claim() -> None:
    """Existing evidence confidence must remain part of grounding policy."""
    result = make_evidence_result(
        confidence=0.60,
    )

    verifier = GroundingVerifier(
        policy=GroundingPolicy(
            minimum_confidence=0.70,
            minimum_supported_claims=1.0,
        )
    )

    support = ClaimSupport(
        claim_id="claim-001",
        evidence_ids=(result.citation.evidence_id,),
        supported=True,
        confidence=result.confidence.value,
    )

    grounding = verifier.verify(
        claims=(make_claim(),),
        supports=(support,),
        evidence_ids={
            result.record.evidence_id,
        },
    )

    assert grounding.grounded is False
    assert grounding.abstain is True


# ============================================================
# Existing provenance contract remains authoritative
# ============================================================


def test_invalid_empty_citation_identity_still_fails() -> None:
    """Phase 7 must preserve the existing citation validation rules."""
    with pytest.raises(ValueError):
        Citation(
            evidence_id="",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=0,
        )


def test_invalid_negative_chunk_index_still_fails() -> None:
    """Phase 7 must preserve chunk-index validation."""
    with pytest.raises(ValueError):
        Citation(
            evidence_id="evidence-001",
            document_id="document-001",
            chunk_id="chunk-001",
            source_path="document.txt",
            chunk_index=-1,
        )
