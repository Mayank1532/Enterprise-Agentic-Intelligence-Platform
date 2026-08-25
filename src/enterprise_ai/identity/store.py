"""Lightweight persistent document identity store."""

import json
from pathlib import Path

from enterprise_ai.identity.registry import IdentityDecision, IdentityStatus


class IdentityStore:
    """Persist document identity decisions as JSON."""

    def __init__(self, path: Path) -> None:
        """Initialize the persistent store."""
        self.path = path

    def load(self) -> dict[str, IdentityDecision]:
        """Load persisted identity decisions."""
        if not self.path.exists():
            return {}

        raw = json.loads(self.path.read_text(encoding="utf-8"))

        return {
            source_path: IdentityDecision(
                status=IdentityStatus(value=data["status"]),
                source_path=data["source_path"],
                content_hash=data["content_hash"],
                version=int(data["version"]),
            )
            for source_path, data in raw.items()
        }

    def save(self, decisions: dict[str, IdentityDecision]) -> None:
        """Persist identity decisions atomically."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            source_path: {
                "status": decision.status.value,
                "source_path": decision.source_path,
                "content_hash": decision.content_hash,
                "version": decision.version,
            }
            for source_path, decision in decisions.items()
        }

        temporary_path = self.path.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        temporary_path.replace(self.path)

    def clear(self) -> None:
        """Remove persisted identity metadata."""
        if self.path.exists():
            self.path.unlink()
