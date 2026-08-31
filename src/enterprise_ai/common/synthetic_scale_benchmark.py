"""Synthetic document workload generation and benchmarking."""

from __future__ import annotations

import hashlib
import time

from enterprise_ai.core.scale_benchmark import (
    ScaleBenchmarkResult,
    SyntheticDocument,
)


class SyntheticScaleBenchmark:
    """Generate deterministic document metadata without filesystem I/O."""

    def __init__(self, partitions: int = 64) -> None:
        """Initialize benchmark configuration."""
        if partitions < 1:
            raise ValueError("partitions must be positive.")

        self._partitions = partitions

    def generate(
        self,
        document_count: int,
        duplicate_every: int | None = None,
    ) -> list[SyntheticDocument]:
        """Generate deterministic synthetic documents."""
        if document_count < 0:
            raise ValueError("document_count must not be negative.")

        if duplicate_every is not None and duplicate_every < 1:
            raise ValueError("duplicate_every must be positive.")

        documents: list[SyntheticDocument] = []

        for index in range(document_count):
            source_index = (
                index - 1
                if duplicate_every is not None
                and index > 0
                and index % duplicate_every == 0
                else index
            )

            document_id = f"doc-{index:012d}"
            payload = f"synthetic-document-{source_index}".encode()
            content_hash = hashlib.sha256(payload).hexdigest()

            partition_key = (
                int(content_hash[:8], 16) % self._partitions
            )

            documents.append(
                SyntheticDocument(
                    document_id=document_id,
                    content_hash=content_hash,
                    partition_key=partition_key,
                    size_bytes=len(payload),
                )
            )

        return documents

    def benchmark(
        self,
        document_count: int,
        duplicate_every: int | None = None,
    ) -> ScaleBenchmarkResult:
        """Generate and benchmark a deterministic synthetic workload."""
        started = time.perf_counter()

        documents = self.generate(
            document_count=document_count,
            duplicate_every=duplicate_every,
        )

        seen_hashes: set[str] = set()
        partition_counts = [0] * self._partitions

        unique_documents = 0

        for document in documents:
            if document.content_hash not in seen_hashes:
                seen_hashes.add(document.content_hash)
                unique_documents += 1

            partition_counts[document.partition_key] += 1

        elapsed = time.perf_counter() - started

        throughput = (
            document_count / elapsed
            if elapsed > 0.0
            else float(document_count)
        )

        return ScaleBenchmarkResult(
            document_count=document_count,
            unique_documents=unique_documents,
            duplicate_documents=document_count - unique_documents,
            elapsed_seconds=elapsed,
            documents_per_second=throughput,
            partitions=self._partitions,
            max_partition_load=max(partition_counts, default=0),
            min_partition_load=min(partition_counts, default=0),
        )
