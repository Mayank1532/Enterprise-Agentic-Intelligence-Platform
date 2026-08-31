"""Provider-neutral evaluation case contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    """One deterministic benchmark case."""

    case_id: str
    query: str
    expected_evidence_ids: tuple[str, ...] = ()
    expected_agent: str | None = None
    expected_tool: str | None = None
    expected_success: bool = True
    expected_abstention: bool = False

    def __post_init__(self) -> None:
        """Validate evaluation case identity."""
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty.")

        if not self.query.strip():
            raise ValueError("query must not be empty.")

        if self.expected_agent is not None and not self.expected_agent.strip():
            raise ValueError("expected_agent must not be empty when provided.")

        if self.expected_tool is not None and not self.expected_tool.strip():
            raise ValueError("expected_tool must not be empty when provided.")

        if any(not evidence_id.strip() for evidence_id in self.expected_evidence_ids):
            raise ValueError("expected evidence IDs must not be empty.")
