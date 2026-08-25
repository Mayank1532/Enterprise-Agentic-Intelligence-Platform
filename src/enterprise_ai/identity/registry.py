"""Deterministic document identity registry."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from enterprise_ai.identity.service import DocumentIdentityService


class IdentityStatus(StrEnum):
    """Classification assigned to an incoming document."""

    NEW = "new"
    DUPLICATE = "duplicate"
    VERSION = "version"


@dataclass(frozen=True)
class IdentityDecision:
    """Result of registering a document."""

    status: IdentityStatus
    source_path: str
    content_hash: str
    version: int


class DocumentIdentityRegistry:
    """Track document identities and deterministic versions."""

    def __init__(
        self,
        identity_service: DocumentIdentityService | None = None,
    ) -> None:
        """Initialize the registry."""
        self.identity_service = identity_service or DocumentIdentityService()

        self._by_source: dict[str, IdentityDecision] = {}
        self._by_hash: dict[str, IdentityDecision] = {}

    def register(self, path: Path) -> IdentityDecision:
        """Register a document and classify it deterministically."""
        identity = self.identity_service.identify(path)

        source_key = str(path.resolve())
        existing_source = self._by_source.get(source_key)

        if existing_source is not None:
            if existing_source.content_hash == identity.content_hash:
                return IdentityDecision(
                    status=IdentityStatus.DUPLICATE,
                    source_path=source_key,
                    content_hash=identity.content_hash,
                    version=existing_source.version,
                )

            version = existing_source.version + 1

            decision = IdentityDecision(
                status=IdentityStatus.VERSION,
                source_path=source_key,
                content_hash=identity.content_hash,
                version=version,
            )

            self._by_source[source_key] = decision
            self._by_hash[identity.content_hash] = decision

            return decision

        existing_hash = self._by_hash.get(identity.content_hash)

        if existing_hash is not None:
            decision = IdentityDecision(
                status=IdentityStatus.DUPLICATE,
                source_path=source_key,
                content_hash=identity.content_hash,
                version=existing_hash.version,
            )

            self._by_source[source_key] = decision

            return decision

        decision = IdentityDecision(
            status=IdentityStatus.NEW,
            source_path=source_key,
            content_hash=identity.content_hash,
            version=1,
        )

        self._by_source[source_key] = decision
        self._by_hash[identity.content_hash] = decision

        return decision

    def get(self, path: Path) -> IdentityDecision | None:
        """Return the registered identity for a source path."""
        return self._by_source.get(str(path.resolve()))

    def clear(self) -> None:
        """Clear all registered identities."""
        self._by_source.clear()
        self._by_hash.clear()
