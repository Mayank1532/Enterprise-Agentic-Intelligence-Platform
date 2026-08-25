"""Phase 2 deterministic regression tests."""

from enterprise_ai.common.bm25_index import BM25Index
from enterprise_ai.common.deterministic_embeddings import (
    DeterministicEmbeddingProvider,
)
from enterprise_ai.common.deterministic_reranker import (
    DeterministicReranker,
)
from enterprise_ai.common.local_vector_index import LocalVectorIndex
from enterprise_ai.core.retrieval import RetrievalRecord


def records() -> tuple[RetrievalRecord, ...]:
    """Create stable regression records."""
    return (
        RetrievalRecord(
            evidence_id="e1",
            document_id="d1",
            chunk_id="c1",
            source_path="a.txt",
            chunk_index=0,
            text="Python retrieval architecture",
        ),
        RetrievalRecord(
            evidence_id="e2",
            document_id="d1",
            chunk_id="c2",
            source_path="a.txt",
            chunk_index=1,
            text="Database storage architecture",
        ),
        RetrievalRecord(
            evidence_id="e3",
            document_id="d2",
            chunk_id="c3",
            source_path="b.txt",
            chunk_index=0,
            text="Python testing strategy",
        ),
    )


def test_bm25_order_is_deterministic() -> None:
    """BM25 repeated execution is stable."""
    index = BM25Index()
    index.add_many(records())

    first = index.search("Python architecture")
    second = index.search("Python architecture")

    assert first == second


def test_vector_order_is_deterministic() -> None:
    """Vector repeated execution is stable."""
    index = LocalVectorIndex(
        DeterministicEmbeddingProvider(),
    )
    index.add_many(records())

    first = index.search("Python architecture")
    second = index.search("Python architecture")

    assert first == second


def test_reranker_order_is_deterministic() -> None:
    """Reranker repeated execution is stable."""
    reranker = DeterministicReranker()

    first = reranker.rerank(
        "Python architecture",
        records(),
    )

    second = reranker.rerank(
        "Python architecture",
        records(),
    )

    assert first == second


def test_embedding_vectors_are_stable() -> None:
    """Embedding vectors remain byte-for-byte equivalent."""
    provider = DeterministicEmbeddingProvider()

    first = provider.embed(
        "Python retrieval architecture",
    )

    second = provider.embed(
        "Python retrieval architecture",
    )

    assert first == second
