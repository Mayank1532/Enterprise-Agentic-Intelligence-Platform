"""Tests for deterministic synthetic scale benchmarking."""

import pytest

from enterprise_ai.common.synthetic_scale_benchmark import (
    SyntheticScaleBenchmark,
)


def test_generation_is_deterministic() -> None:
    benchmark = SyntheticScaleBenchmark(partitions=8)

    first = benchmark.generate(100)
    second = benchmark.generate(100)

    assert first == second


def test_generation_has_expected_size() -> None:
    benchmark = SyntheticScaleBenchmark(partitions=8)

    documents = benchmark.generate(250)

    assert len(documents) == 250


def test_partition_keys_are_bounded() -> None:
    benchmark = SyntheticScaleBenchmark(partitions=16)

    documents = benchmark.generate(500)

    assert all(0 <= document.partition_key < 16 for document in documents)


def test_duplicate_detection() -> None:
    benchmark = SyntheticScaleBenchmark(partitions=8)

    result = benchmark.benchmark(
        document_count=100,
        duplicate_every=10,
    )

    assert result.document_count == 100
    assert result.duplicate_documents > 0
    assert result.unique_documents < result.document_count


def test_zero_document_benchmark() -> None:
    benchmark = SyntheticScaleBenchmark(partitions=8)

    result = benchmark.benchmark(0)

    assert result.document_count == 0
    assert result.unique_documents == 0
    assert result.duplicate_documents == 0
    assert result.documents_per_second == 0.0


def test_invalid_partition_count() -> None:
    with pytest.raises(ValueError, match="partitions"):
        SyntheticScaleBenchmark(partitions=0)


def test_invalid_document_count() -> None:
    benchmark = SyntheticScaleBenchmark()

    with pytest.raises(ValueError, match="document_count"):
        benchmark.generate(-1)


def test_invalid_duplicate_interval() -> None:
    benchmark = SyntheticScaleBenchmark()

    with pytest.raises(ValueError, match="duplicate_every"):
        benchmark.generate(10, duplicate_every=0)
