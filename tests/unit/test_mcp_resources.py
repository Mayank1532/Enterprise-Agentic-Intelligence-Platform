"""Tests for deterministic MCP resources."""

from enterprise_ai.mcp.resources import (
    PLATFORM_STATUS_RESOURCE_URI,
    get_platform_status_resource,
)
from enterprise_ai.mcp.server import (
    create_mcp_server,
    mcp_server,
)


EXPECTED_RESOURCE = "platform=enterprise-ai\nstatus=operational\nexecution_mode=deterministic"


def test_platform_status_resource_is_deterministic() -> None:
    """Resource content is deterministic."""
    first = get_platform_status_resource()
    second = get_platform_status_resource()

    assert first == second


def test_platform_status_resource_contract() -> None:
    """Resource exposes the canonical platform status."""
    assert get_platform_status_resource() == EXPECTED_RESOURCE


def test_platform_status_resource_uri_is_canonical() -> None:
    """Resource uses the canonical URI."""
    assert PLATFORM_STATUS_RESOURCE_URI == "platform://status"


def test_mcp_server_can_be_created_with_resource() -> None:
    """Server can be created with registered resources."""
    server = create_mcp_server()

    assert server is not None


def test_global_mcp_server_is_available() -> None:
    """Configured MCP server remains available."""
    assert mcp_server is not None
