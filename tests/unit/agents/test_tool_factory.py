"""Tests for the ADK tool factory."""

from unittest.mock import Mock

from enterprise_ai.agents.adk.retrieval_tool import (
    RetrievalTool,
)
from enterprise_ai.agents.adk.tool_factory import (
    build_retrieval_function_tool,
)


def test_factory_returns_callable() -> None:
    """Factory returns a callable ADK tool boundary."""
    tool = RetrievalTool(Mock())

    function_tool = build_retrieval_function_tool(tool)

    assert callable(function_tool)


def test_factory_returns_search_function() -> None:
    """Factory exposes the retrieval tool search method."""
    tool = RetrievalTool(Mock())

    function_tool = build_retrieval_function_tool(tool)

    assert function_tool == tool.search
