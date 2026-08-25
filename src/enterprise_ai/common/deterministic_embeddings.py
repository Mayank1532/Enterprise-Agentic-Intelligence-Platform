"""Deterministic local embedding provider."""

import hashlib
import math
from collections.abc import Sequence


class DeterministicEmbeddingProvider:
    """Create stable local vectors without external model dependencies."""

    def __init__(self, dimensions: int = 64) -> None:
        """Initialize the deterministic embedding provider."""
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")

        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        """Return embedding dimensionality."""
        return self._dimensions

    def embed(self, text: str) -> tuple[float, ...]:
        """Create a deterministic normalized vector."""
        values = [0.0] * self._dimensions

        tokens = text.lower().split()

        if not tokens:
            return tuple(values)

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()

            index = (
                int.from_bytes(
                    digest[:4],
                    byteorder="big",
                )
                % self._dimensions
            )

            sign = 1.0 if digest[4] % 2 == 0 else -1.0

            values[index] += sign

        norm = math.sqrt(sum(value * value for value in values))

        if norm == 0:
            return tuple(values)

        return tuple(value / norm for value in values)

    def embed_many(
        self,
        texts: Sequence[str],
    ) -> tuple[tuple[float, ...], ...]:
        """Create deterministic embeddings for multiple texts."""
        return tuple(self.embed(text) for text in texts)
