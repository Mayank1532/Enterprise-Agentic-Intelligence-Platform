"""Tests for the deterministic MCP capability policy."""

import pytest

from enterprise_ai.mcp.capability_policy import (
    MCPCapabilityError,
    validate_tool_call,
)


def test_platform_status_is_allowed_without_arguments() -> None:
    """The canonical platform status capability is allowed."""
    validate_tool_call(
        "platform_status",
        {},
    )


def test_platform_status_is_allowed_with_none_arguments() -> None:
    """The canonical capability accepts omitted arguments."""
    validate_tool_call(
        "platform_status",
        None,
    )


def test_unknown_tool_is_denied() -> None:
    """Unknown capabilities are denied by default."""
    with pytest.raises(
        MCPCapabilityError,
        match="not an allowed capability",
    ):
        validate_tool_call(
            "unknown_tool",
            {},
        )


def test_platform_status_rejects_arguments() -> None:
    """The zero-argument capability rejects unexpected arguments."""
    with pytest.raises(
        MCPCapabilityError,
        match="invalid arguments",
    ):
        validate_tool_call(
            "platform_status",
            {
                "unexpected": "value",
            },
        )


def test_platform_status_rejects_multiple_arguments() -> None:
    """The capability cannot receive arbitrary argument payloads."""
    with pytest.raises(
        MCPCapabilityError,
        match="invalid arguments",
    ):
        validate_tool_call(
            "platform_status",
            {
                "query": "status",
                "extra": True,
            },
        )
