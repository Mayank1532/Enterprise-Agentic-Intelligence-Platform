"""Contracts for incremental document ingestion state."""

from dataclasses import dataclass
from enum import StrEnum


class IngestionAction(StrEnum):
    """Action required for a document."""

    CREATE = "create"
    UPDATE = "update"
    SKIP = "skip"


@dataclass(frozen=True, slots=True)
class DocumentState:
    """Persistable identity and content state for a document."""

    document_id: str
    content_hash: str
    version: int

    def __post_init__(self) -> None:
        """Validate document state."""
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty.")

        if not self.content_hash.strip():
            raise ValueError("content_hash must not be empty.")

        if self.version < 1:
            raise ValueError("version must be positive.")


@dataclass(frozen=True, slots=True)
class IngestionDecision:
    """Deterministic decision for an incoming document."""

    action: IngestionAction
    document_id: str
    previous_version: int | None
    new_version: int | None

    def __post_init__(self) -> None:
        """Validate decision invariants."""
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty.")

        if self.action is IngestionAction.SKIP:
            if self.new_version is not None:
                raise ValueError(
                    "skip decisions must not define a new version."
                )

        if self.action in (
            IngestionAction.CREATE,
            IngestionAction.UPDATE,
        ):
            if self.new_version is None:
                raise ValueError(
                    "create/update decisions require a new version."
                )
