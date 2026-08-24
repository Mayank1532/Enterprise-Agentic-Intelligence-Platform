"""Incremental processing cache."""

import hashlib
import sqlite3
from pathlib import Path


class ProcessingCache:
    """Persist processed content fingerprints and results locally."""

    def __init__(self, path: str = "data/cache/processing.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

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

        return None if row is None else str(row[0])

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
