"""Agent and tool selection evaluation contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentToolSelectionOutcome:
    """Observed agent/tool selection for one evaluation case."""

    case_id: str
    selected_agent: str | None
    selected_tool: str | None
    correct: bool

    def __post_init__(self) -> None:
        """Validate selection outcome identity."""
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty.")

        if self.selected_agent is not None and not self.selected_agent.strip():
            raise ValueError("selected_agent must not be empty when provided.")

        if self.selected_tool is not None and not self.selected_tool.strip():
            raise ValueError("selected_tool must not be empty when provided.")
