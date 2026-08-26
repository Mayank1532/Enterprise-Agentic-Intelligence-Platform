"""ADK function-tool boundary."""

from collections.abc import Callable

from enterprise_ai.agents.adk.retrieval_tool import (
    RetrievalTool,
)
from enterprise_ai.core.tool_result import (
    ToolResult,
)


def build_retrieval_function_tool(
    retrieval_tool: RetrievalTool,
) -> Callable[[str, int], ToolResult]:
    """Return the callable used by Google ADK."""
    return retrieval_tool.search
