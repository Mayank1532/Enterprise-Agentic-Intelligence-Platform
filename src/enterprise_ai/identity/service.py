"""Deterministic document identity and versioning utilities."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class DocumentIdentity:
    """Stable identity information for a document."""

    content_hash: str
    size_bytes: int
    version: int


class DocumentIdentityService:
    """Compute deterministic document identity without loading full files."""

    def __init__(self, read_chunk_size: int = 64 * 1024) -> None:
        """Initialize the identity service."""
        if read_chunk_size <= 0:
            raise ValueError("read_chunk_size must be greater than zero")

        self.read_chunk_size = read_chunk_size

    def content_hash(self, path: Path) -> str:
        """Return the SHA-256 hash of a file using bounded memory."""
        if not path.is_file():
            raise FileNotFoundError(f"Source file not found: {path}")

        digest = sha256()

        with path.open("rb") as file:
            while True:
                chunk = file.read(self.read_chunk_size)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    def identify(self, path: Path, version: int = 1) -> DocumentIdentity:
        """Return deterministic identity information for a file."""
        if version < 1:
            raise ValueError("version must be greater than or equal to one")

        return DocumentIdentity(
            content_hash=self.content_hash(path),
            size_bytes=path.stat().st_size,
            version=version,
        )

    def is_same_content(
        self,
        first_path: Path,
        second_path: Path,
    ) -> bool:
        """Return whether two files contain identical bytes."""
        return self.content_hash(first_path) == self.content_hash(second_path)
