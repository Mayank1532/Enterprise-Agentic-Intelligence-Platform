"""Tests for deterministic structured output."""

import pytest
from pydantic import ValidationError

from enterprise_ai.common.structured_output_builder import (
    StructuredOutputBuilder,
)
from enterprise_ai.core.evidence import EvidenceBlock


def make_evidence() -> EvidenceBlock:
    """Create deterministic evidence."""
    return EvidenceBlock(
        evidence_id="evidence-001",
        document_id="document-001",
        chunk_id="chunk-001",
        source_path="document.txt",
        chunk_index=0,
        text="Verified evidence.",
    )


def test_supported_output_contains_evidence() -> None:
    """Supported output requires and preserves evidence."""
    result = StructuredOutputBuilder.supported(
        answer="Verified answer.",
        confidence=0.95,
        evidence=(make_evidence(),),
    )

    assert result.status == "supported"
    assert result.result.supported is True
    assert result.result.answer == "Verified answer."
    assert result.result.confidence == 0.95
    assert len(result.result.evidence) == 1
    assert result.result.evidence[0].evidence_id == "evidence-001"


def test_refused_output_is_explicit() -> None:
    """Insufficient evidence produces explicit refusal."""
    result = StructuredOutputBuilder.refused(
        reason="insufficient evidence",
    )

    assert result.status == "refused"
    assert result.result.supported is False
    assert result.result.is_refusal() is True
    assert result.result.refusal_reason == "insufficient evidence"
    assert result.result.evidence == ()


def test_supported_output_without_evidence_fails() -> None:
    """Supported output cannot exist without evidence."""
    with pytest.raises(ValueError, match="evidence"):
        StructuredOutputBuilder.supported(
            answer="Unsupported answer.",
            confidence=0.5,
            evidence=(),
        )


def test_confidence_must_be_between_zero_and_one() -> None:
    """Confidence is strictly bounded."""
    with pytest.raises(ValidationError):
        StructuredOutputBuilder.supported(
            answer="Answer.",
            confidence=1.5,
            evidence=(make_evidence(),),
        )


def test_negative_confidence_is_rejected() -> None:
    """Negative confidence is invalid."""
    with pytest.raises(ValidationError):
        StructuredOutputBuilder.supported(
            answer="Answer.",
            confidence=-0.1,
            evidence=(make_evidence(),),
        )


def test_supported_envelope_rejects_refused_answer() -> None:
    """Supported envelope cannot wrap a refusal."""
    refused = StructuredOutputBuilder.refused(
        reason="insufficient evidence",
    )

    with pytest.raises(ValueError, match="Supported envelope"):
        from enterprise_ai.core.structured_output import (
            AgentOutputEnvelope,
        )

        AgentOutputEnvelope.supported_result(
            refused.result,
        )


def test_refused_envelope_rejects_supported_answer() -> None:
    """Refused envelope cannot wrap a supported answer."""
    supported = StructuredOutputBuilder.supported(
        answer="Verified answer.",
        confidence=0.9,
        evidence=(make_evidence(),),
    )

    with pytest.raises(ValueError, match="Refused envelope"):
        from enterprise_ai.core.structured_output import (
            AgentOutputEnvelope,
        )

        AgentOutputEnvelope.refused_result(
            supported.result,
        )


def test_structured_output_is_immutable() -> None:
    """Structured output models are immutable."""
    result = StructuredOutputBuilder.refused(
        reason="insufficient evidence",
    )

    with pytest.raises(ValidationError):
        result.result.answer = "changed"
