"""ADK-compatible callback adapters."""

from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from enterprise_ai.agents.adk.agent_callbacks import (
    AgentLifecyclePolicy,
)
from enterprise_ai.agents.adk.tool_callbacks import (
    ToolLifecyclePolicy,
)


def before_agent_callback(
    context: CallbackContext,
) -> None:
    """Run deterministic before-agent policy without overriding ADK."""
    AgentLifecyclePolicy().before_agent(context)
    return None


def after_agent_callback(
    context: CallbackContext,
) -> None:
    """Run deterministic after-agent audit without overriding ADK."""
    AgentLifecyclePolicy().after_agent(context)
    return None


def before_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> None:
    """Run deterministic before-tool policy without overriding ADK."""
    del tool, args
    ToolLifecyclePolicy().before_tool(tool_context)
    return None


def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> None:
    """Run deterministic after-tool audit without overriding ADK."""
    del tool, args, tool_response
    ToolLifecyclePolicy().after_tool(tool_context)
    return None
