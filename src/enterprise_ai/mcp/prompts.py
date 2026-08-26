"""Deterministic MCP prompts for the Enterprise AI platform."""

from mcp.server import MCPServer

PLATFORM_ANALYSIS_PROMPT_NAME = "platform_analysis"


def render_platform_analysis_prompt(topic: str) -> str:
    """Render the canonical platform-analysis prompt."""
    normalized_topic = topic.strip()

    if not normalized_topic:
        raise ValueError("topic must not be empty")

    return (
        "Analyze the following Enterprise AI platform topic using "
        "evidence-first reasoning:\n\n"
        f"Topic: {normalized_topic}\n\n"
        "Requirements:\n"
        "- distinguish facts from assumptions\n"
        "- identify supporting evidence\n"
        "- identify uncertainty explicitly\n"
        "- do not invent unavailable information"
    )


def register_prompts(server: MCPServer) -> None:
    """Register platform prompts on the supplied MCP server."""

    @server.prompt(
        name=PLATFORM_ANALYSIS_PROMPT_NAME,
        title="Platform Analysis",
        description="Create an evidence-first analysis request for a platform topic.",
    )
    def platform_analysis(topic: str) -> str:
        """Create an evidence-first platform analysis request."""
        return render_platform_analysis_prompt(topic)
