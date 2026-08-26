"""Deterministic structured response models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceReference(BaseModel):
    """Reference to evidence supporting a response."""

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    source_path: str = Field(min_length=1)


class StructuredAnswer(BaseModel):
    """Validated answer produced from available evidence."""

    model_config = ConfigDict(frozen=True)

    answer: str
    supported: bool
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: tuple[EvidenceReference, ...] = ()
    refusal_reason: str | None = None

    def is_refusal(self) -> bool:
        """Return whether the answer is an explicit refusal."""
        return not self.supported


class AgentOutputEnvelope(BaseModel):
    """Stable top-level contract for future ADK agent output."""

    model_config = ConfigDict(frozen=True)

    status: Literal["supported", "refused"]
    result: StructuredAnswer

    @classmethod
    def supported_result(
        cls,
        answer: StructuredAnswer,
    ) -> "AgentOutputEnvelope":
        """Create a supported result envelope."""
        if not answer.supported:
            raise ValueError("Supported envelope requires supported answer.")

        return cls(
            status="supported",
            result=answer,
        )

    @classmethod
    def refused_result(
        cls,
        answer: StructuredAnswer,
    ) -> "AgentOutputEnvelope":
        """Create a refusal result envelope."""
        if answer.supported:
            raise ValueError("Refused envelope requires unsupported answer.")

        return cls(
            status="refused",
            result=answer,
        )
