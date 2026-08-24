"""Incremental processing cache."""

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CacheStats:
    """Cache usage statistics."""

    hits: int
    misses: int
    stored: int

    @property
    def total_lookups(self) -> int:
        """Return total cache lookups."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Return cache hit rate."""
        total = self.total_lookups

        if total == 0:
            return 0.0

        return self.hits / total


class ProcessingCache:
    """Persist processed content fingerprints and results locally."""

    def __init__(self, path: str = "data/cache/processing.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._hits = 0
        self._misses = 0
        self._stored = 0

        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_items (
                    content_hash TEXT PRIMARY KEY,
                    result TEXT NOT NULL
                )
                """
            )
            connection.commit()

    @staticmethod
    def fingerprint(content: bytes) -> str:
        """Return a stable SHA-256 fingerprint for content."""
        return hashlib.sha256(content).hexdigest()

    def get(self, content_hash: str) -> str | None:
        """Return a cached result when available."""
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                """
                SELECT result
                FROM processed_items
                WHERE content_hash = ?
                """,
                (content_hash,),
            ).fetchone()

        if row is None:
            self._misses += 1
            return None

        self._hits += 1
        return str(row[0])

    def put(self, content_hash: str, result: str) -> None:
        """Store or replace a processed result."""
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO processed_items(content_hash, result)
                VALUES (?, ?)
                ON CONFLICT(content_hash)
                DO UPDATE SET result = excluded.result
                """,
                (content_hash, result),
            )
            connection.commit()

        self._stored += 1

    def stats(self) -> CacheStats:
        """Return cache usage statistics."""
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            stored=self._stored,
        )
