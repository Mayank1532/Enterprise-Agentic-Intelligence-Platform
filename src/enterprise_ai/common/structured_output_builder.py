"""Deterministic structured-output construction."""

from collections.abc import Iterable

from enterprise_ai.core.evidence import EvidenceBlock
from enterprise_ai.core.structured_output import (
    AgentOutputEnvelope,
    EvidenceReference,
    StructuredAnswer,
)


class StructuredOutputBuilder:
    """Build validated structured responses from evidence."""

    @staticmethod
    def supported(
        answer: str,
        confidence: float,
        evidence: Iterable[EvidenceBlock],
    ) -> AgentOutputEnvelope:
        """Build a supported structured response."""
        references = tuple(
            EvidenceReference(
                evidence_id=item.evidence_id,
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                source_path=item.source_path,
            )
            for item in evidence
        )

        if not references:
            raise ValueError("Supported output requires at least one evidence reference.")

        result = StructuredAnswer(
            answer=answer,
            supported=True,
            confidence=confidence,
            evidence=references,
        )

        return AgentOutputEnvelope.supported_result(result)

    @staticmethod
    def refused(
        reason: str,
    ) -> AgentOutputEnvelope:
        """Build an explicit refusal response."""
        result = StructuredAnswer(
            answer="",
            supported=False,
            confidence=0.0,
            evidence=(),
            refusal_reason=reason,
        )

        return AgentOutputEnvelope.refused_result(result)
