"""Resource-conscious file processing."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from enterprise_ai.common.processing_cache import ProcessingCache


@dataclass(frozen=True)
class ProcessingResult:
    """Result of processing a file."""

    content_hash: str
    size_bytes: int
    reused: bool


class FileProcessor:
    """Process files without loading their complete contents into memory."""

    def __init__(
        self,
        cache: ProcessingCache,
        chunk_size: int = 1024 * 1024,
        max_file_size: int = 100 * 1024 * 1024,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if max_file_size <= 0:
            raise ValueError("max_file_size must be greater than zero")

        self.cache = cache
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size

    def process(self, path: Path) -> ProcessingResult:
        """Process a file incrementally."""
        if not path.is_file():
            raise FileNotFoundError(path)

        size = path.stat().st_size

        if size > self.max_file_size:
            raise ValueError(
                f"File exceeds configured maximum size: {self.max_file_size} bytes"
            )

        digest = hashlib.sha256()

        with path.open("rb") as file:
            while chunk := file.read(self.chunk_size):
                digest.update(chunk)

        content_hash = digest.hexdigest()
        cached_result = self.cache.get(content_hash)

        if cached_result is not None:
            return ProcessingResult(
                content_hash=content_hash,
                size_bytes=size,
                reused=True,
            )

        result = f"processed:{content_hash}:{size}"

        self.cache.put(content_hash, result)

        return ProcessingResult(
            content_hash=content_hash,
            size_bytes=size,
            reused=False,
        )
