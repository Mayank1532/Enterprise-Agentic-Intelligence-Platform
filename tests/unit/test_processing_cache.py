"""Processing cache tests."""

from enterprise_ai.common.processing_cache import ProcessingCache


def test_same_content_produces_same_fingerprint(tmp_path) -> None:
    """Identical content must produce an identical fingerprint."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    first = cache.fingerprint(b"enterprise intelligence")
    second = cache.fingerprint(b"enterprise intelligence")

    assert first == second


def test_different_content_produces_different_fingerprint(tmp_path) -> None:
    """Different content must produce different fingerprints."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    first = cache.fingerprint(b"document A")
    second = cache.fingerprint(b"document B")

    assert first != second


def test_cached_result_is_reused(tmp_path) -> None:
    """A previously processed result must be reusable."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    content_hash = cache.fingerprint(b"document")

    assert cache.get(content_hash) is None

    cache.put(content_hash, "processed-result")

    assert cache.get(content_hash) == "processed-result"


def test_changed_content_requires_new_processing(tmp_path) -> None:
    """Changed content must receive a different cache key."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    original = cache.fingerprint(b"document version 1")
    changed = cache.fingerprint(b"document version 2")

    cache.put(original, "version-1-result")

    assert cache.get(original) == "version-1-result"
    assert cache.get(changed) is None


def test_cache_statistics_measure_hits_and_misses(tmp_path) -> None:
    """Cache statistics must measure avoided processing."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    content_hash = cache.fingerprint(b"document")

    assert cache.get(content_hash) is None

    cache.put(content_hash, "processed-result")

    assert cache.get(content_hash) == "processed-result"

    stats = cache.stats()

    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.stored == 1
    assert stats.total_lookups == 2
    assert stats.hit_rate == 0.5


def test_empty_cache_has_zero_hit_rate(tmp_path) -> None:
    """An unused cache must report a zero hit rate."""
    cache = ProcessingCache(str(tmp_path / "cache.db"))

    stats = cache.stats()

    assert stats.total_lookups == 0
    assert stats.hit_rate == 0.0
