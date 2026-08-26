"""Deterministic capability policy for the MCP client boundary."""

from typing import Any


class MCPCapabilityError(RuntimeError):
    """Raised when an MCP capability request violates the policy."""


_ALLOWED_TOOL_ARGUMENTS: dict[str, frozenset[str]] = {
    "platform_status": frozenset(),
}


def validate_tool_call(
    name: str,
    arguments: dict[str, Any] | None,
) -> None:
    """Validate an MCP tool call before it reaches the MCP SDK.

    The policy is intentionally deterministic and deny-by-default.

    Only the explicitly registered capability ``platform_status`` is
    permitted, and that capability accepts no arguments.
    """
    if name not in _ALLOWED_TOOL_ARGUMENTS:
        raise MCPCapabilityError(
            f"MCP tool '{name}' is not an allowed capability."
        )

    provided_arguments = arguments or {}

    if set(provided_arguments) != set(_ALLOWED_TOOL_ARGUMENTS[name]):
        raise MCPCapabilityError(
            f"MCP tool '{name}' received invalid arguments."
        )
