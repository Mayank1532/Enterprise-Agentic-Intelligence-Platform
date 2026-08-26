"""ADK tool integration smoke tests."""

from unittest.mock import Mock

from google.adk.tools import FunctionTool

from enterprise_ai.agents.adk.retrieval_tool import (
    RetrievalTool,
)
from enterprise_ai.agents.adk.tool_factory import (
    build_retrieval_function_tool,
)


def test_retrieval_function_can_be_wrapped_by_adk() -> None:
    """Retrieval callable can be wrapped as an ADK FunctionTool."""
    retrieval_tool = RetrievalTool(Mock())

    function = build_retrieval_function_tool(
        retrieval_tool,
    )

    tool = FunctionTool(func=function)

    assert tool.func == function
