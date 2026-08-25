"""Persistent document identity registry."""

from pathlib import Path

from enterprise_ai.identity.registry import (
    DocumentIdentityRegistry,
    IdentityDecision,
)


class PersistentDocumentIdentityRegistry:
    """Document identity registry backed by a lightweight JSON store."""

    def __init__(
        self,
        store_path: Path,
    ) -> None:
        """Initialize the persistent registry."""
        from enterprise_ai.identity.store import IdentityStore

        self.store = IdentityStore(store_path)
        self._decisions = self.store.load()

        self._registry = DocumentIdentityRegistry()

    def register(self, path: Path) -> IdentityDecision:
        """Register a document and persist its identity decision."""
        source_key = str(path.resolve())

        decision = self._register_using_persisted_state(path, source_key)

        self._decisions[source_key] = decision
        self.store.save(self._decisions)

        return decision

    def get(self, path: Path) -> IdentityDecision | None:
        """Return the persisted decision for a document."""
        return self._decisions.get(str(path.resolve()))

    def clear(self) -> None:
        """Clear persistent identity metadata."""
        self._decisions.clear()
        self._registry.clear()
        self.store.clear()

    def _register_using_persisted_state(
        self,
        path: Path,
        source_key: str,
    ) -> IdentityDecision:
        """Classify a document using persisted identity information."""
        identity = self._registry.identity_service.identify(path)

        existing = self._decisions.get(source_key)

        if existing is not None:
            if existing.content_hash == identity.content_hash:
                from enterprise_ai.identity.registry import IdentityDecision, IdentityStatus

                return IdentityDecision(
                    status=IdentityStatus.DUPLICATE,
                    source_path=source_key,
                    content_hash=identity.content_hash,
                    version=existing.version,
                )

            from enterprise_ai.identity.registry import IdentityDecision, IdentityStatus

            return IdentityDecision(
                status=IdentityStatus.VERSION,
                source_path=source_key,
                content_hash=identity.content_hash,
                version=existing.version + 1,
            )

        for decision in self._decisions.values():
            if decision.content_hash == identity.content_hash:
                from enterprise_ai.identity.registry import IdentityDecision, IdentityStatus

                return IdentityDecision(
                    status=IdentityStatus.DUPLICATE,
                    source_path=source_key,
                    content_hash=identity.content_hash,
                    version=decision.version,
                )

        from enterprise_ai.identity.registry import IdentityDecision, IdentityStatus

        return IdentityDecision(
            status=IdentityStatus.NEW,
            source_path=source_key,
            content_hash=identity.content_hash,
            version=1,
        )
