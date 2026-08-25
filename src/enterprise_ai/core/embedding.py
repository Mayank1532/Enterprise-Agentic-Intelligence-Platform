"""Embedding provider contracts."""

from collections.abc import Sequence
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Provider-neutral embedding interface."""

    @property
    def dimensions(self) -> int:
        """Return embedding dimensionality."""
        ...

    def embed(self, text: str) -> tuple[float, ...]:
        """Create an embedding for text."""
        ...

    def embed_many(
        self,
        texts: Sequence[str],
    ) -> tuple[tuple[float, ...], ...]:
        """Create embeddings for multiple texts."""
        ...
