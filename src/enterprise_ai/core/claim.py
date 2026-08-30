"""Domain contract for an answer claim."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    """A factual claim that can be checked against evidence."""

    claim_id: str
    text: str

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id must not be empty.")

        if not self.text.strip():
            raise ValueError("claim text must not be empty.")
