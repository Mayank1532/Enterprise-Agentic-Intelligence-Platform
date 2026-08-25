"""Tests for the deterministic embedding provider."""

from enterprise_ai.common.deterministic_embeddings import (
    DeterministicEmbeddingProvider,
)


def test_embedding_is_deterministic() -> None:
    """The same text always produces the same vector."""
    provider = DeterministicEmbeddingProvider()

    assert provider.embed("Python retrieval") == provider.embed("Python retrieval")


def test_embedding_dimensions_are_stable() -> None:
    """Vectors have the configured dimensionality."""
    provider = DeterministicEmbeddingProvider(dimensions=32)

    assert len(provider.embed("test")) == 32
    assert provider.dimensions == 32


def test_empty_embedding_is_zero_vector() -> None:
    """Empty input produces a zero vector."""
    provider = DeterministicEmbeddingProvider(dimensions=16)

    assert provider.embed("") == (0.0,) * 16


def test_embed_many_matches_individual_embedding() -> None:
    """Batch embedding matches individual embedding."""
    provider = DeterministicEmbeddingProvider()

    texts = (
        "first document",
        "second document",
    )

    assert provider.embed_many(texts) == tuple(provider.embed(text) for text in texts)


def test_invalid_dimension_fails_fast() -> None:
    """Non-positive dimensions are rejected."""
    try:
        DeterministicEmbeddingProvider(dimensions=0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
