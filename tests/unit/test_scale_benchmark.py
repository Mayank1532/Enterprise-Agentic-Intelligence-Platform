"""Scale benchmark result contract tests."""

import pytest

from enterprise_ai.core.scale_benchmark import ScaleBenchmarkResult


def test_scale_result_invariants() -> None:
    result = ScaleBenchmarkResult(
        document_count=100,
        unique_documents=90,
        duplicate_documents=10,
        elapsed_seconds=1.0,
        documents_per_second=100.0,
        partitions=8,
        max_partition_load=20,
        min_partition_load=5,
    )

    assert result.unique_documents + result.duplicate_documents == 100


def test_scale_result_rejects_inconsistent_counts() -> None:
    with pytest.raises(ValueError, match="must equal"):
        ScaleBenchmarkResult(
            document_count=100,
            unique_documents=80,
            duplicate_documents=5,
            elapsed_seconds=1.0,
            documents_per_second=100.0,
            partitions=8,
            max_partition_load=20,
            min_partition_load=5,
        )
