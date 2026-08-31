"""Task success evaluation contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskOutcome:
    """Observed result of one benchmark task."""

    case_id: str
    succeeded: bool
    failed: bool
    abstained: bool

    def __post_init__(self) -> None:
        """Validate task outcome identity and state."""
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty.")

        if self.succeeded and self.failed:
            raise ValueError("A task cannot be both succeeded and failed.")

        if self.succeeded and self.abstained:
            raise ValueError("A successful task cannot be abstained.")
