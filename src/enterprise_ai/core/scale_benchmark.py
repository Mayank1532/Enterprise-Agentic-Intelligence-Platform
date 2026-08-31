"""Deterministic synthetic scale benchmark contracts."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SyntheticDocument:
    """Minimal synthetic document metadata."""

    document_id: str
    content_hash: str
    partition_key: int
    size_bytes: int


@dataclass(frozen=True, slots=True)
class ScaleBenchmarkResult:
    """Measured synthetic workload result."""

    document_count: int
    unique_documents: int
    duplicate_documents: int
    elapsed_seconds: float
    documents_per_second: float
    partitions: int
    max_partition_load: int
    min_partition_load: int

    def __post_init__(self) -> None:
        """Validate benchmark invariants."""
        if self.document_count < 0:
            raise ValueError("document_count must not be negative.")

        if self.unique_documents < 0:
            raise ValueError("unique_documents must not be negative.")

        if self.duplicate_documents < 0:
            raise ValueError("duplicate_documents must not be negative.")

        if self.unique_documents + self.duplicate_documents != self.document_count:
            raise ValueError(
                "unique_documents + duplicate_documents "
                "must equal document_count."
            )

        if self.elapsed_seconds < 0.0:
            raise ValueError("elapsed_seconds must not be negative.")

        if self.documents_per_second < 0.0:
            raise ValueError("documents_per_second must not be negative.")

        if self.partitions < 1:
            raise ValueError("partitions must be positive.")

        if self.max_partition_load < 0:
            raise ValueError("max_partition_load must not be negative.")

        if self.min_partition_load < 0:
            raise ValueError("min_partition_load must not be negative.")
