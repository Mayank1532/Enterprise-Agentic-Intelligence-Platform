"""Identity-aware ingestion coordination."""

from pathlib import Path

from enterprise_ai.identity.persistent_registry import (
    PersistentDocumentIdentityRegistry,
)
from enterprise_ai.identity.registry import IdentityDecision


class IdentityAwareIngestionCoordinator:
    """Coordinate ingestion classification through persistent identity."""

    def __init__(
        self,
        registry: PersistentDocumentIdentityRegistry,
    ) -> None:
        """Initialize the coordinator."""
        self._registry = registry

    def classify(self, path: Path) -> IdentityDecision:
        """Classify a document using persistent identity metadata."""
        return self._registry.register(path)

    def get(self, path: Path) -> IdentityDecision | None:
        """Return persisted identity metadata for a document."""
        return self._registry.get(path)

    def clear(self) -> None:
        """Clear persisted identity metadata."""
        self._registry.clear()
