"""Tests for MCP failure isolation at the ADK boundary."""

import asyncio

import pytest

from enterprise_ai.agents.adk.mcp_agent import (
    create_mcp_enabled_agent,
)
from enterprise_ai.agents.adk.mcp_exceptions import (
    MCPIntegrationError,
)
from enterprise_ai.agents.adk.mcp_tools import (
    mcp_platform_status_tool,
)

EXPECTED_STATUS = {
    "platform": "enterprise-ai",
    "status": "operational",
    "execution_mode": "deterministic",
}


class FakeErrorResult:
    """Fake MCP result representing an MCP tool failure."""

    is_error = True
    structured_content = None


class FakeEmptyResult:
    """Fake MCP result with no structured content."""

    is_error = False
    structured_content = None


class FakeMalformedResult:
    """Fake MCP result with malformed structured content."""

    is_error = False
    structured_content = ["not", "a", "dictionary"]


class FakeSuccessfulResult:
    """Fake MCP result representing successful MCP execution."""

    is_error = False
    structured_content = EXPECTED_STATUS


class FakeMCPClient:
    """Fake async MCP client used to isolate adapter behavior."""

    result: object = FakeSuccessfulResult()
    error: Exception | None = None

    def __init__(self) -> None:
        """Initialize the fake client."""
        self._entered = False

    async def __aenter__(self) -> "FakeMCPClient":
        """Enter the fake client session."""
        self._entered = True

        if self.error is not None:
            raise self.error

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit the fake client session."""
        self._entered = False

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, object],
    ) -> object:
        """Return the configured fake result."""
        return self.result


def run_tool_with_fake_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_client: type[FakeMCPClient],
) -> object:
    """Execute the adapter with a fake MCP client."""

    import enterprise_ai.agents.adk.mcp_tools as module

    monkeypatch.setattr(
        module,
        "MCPPlatformClient",
        fake_client,
    )

    return asyncio.run(mcp_platform_status_tool())


def test_successful_mcp_result_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful MCP results pass through unchanged."""

    result = run_tool_with_fake_client(
        monkeypatch,
        FakeMCPClient,
    )

    assert result == EXPECTED_STATUS


def test_mcp_error_result_becomes_integration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An MCP error result becomes an explicit integration error."""

    class ErrorClient(FakeMCPClient):
        result = FakeErrorResult()

    with pytest.raises(
        MCPIntegrationError,
        match="returned an error",
    ):
        run_tool_with_fake_client(
            monkeypatch,
            ErrorClient,
        )


def test_missing_structured_content_becomes_integration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing structured content is never treated as success."""

    class EmptyClient(FakeMCPClient):
        result = FakeEmptyResult()

    with pytest.raises(
        MCPIntegrationError,
        match="no structured content",
    ):
        run_tool_with_fake_client(
            monkeypatch,
            EmptyClient,
        )


def test_malformed_structured_content_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed MCP structured content is rejected explicitly."""

    class MalformedClient(FakeMCPClient):
        result = FakeMalformedResult()

    with pytest.raises(
        TypeError,
        match="must return a dictionary",
    ):
        run_tool_with_fake_client(
            monkeypatch,
            MalformedClient,
        )


def test_client_exception_becomes_integration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Client/session exceptions are isolated at the ADK boundary."""

    class FailingClient(FakeMCPClient):
        error = ConnectionError("simulated MCP connection failure")

    with pytest.raises(
        MCPIntegrationError,
        match="MCP platform status operation failed",
    ) as exc_info:
        run_tool_with_fake_client(
            monkeypatch,
            FailingClient,
        )

    assert isinstance(
        exc_info.value.__cause__,
        ConnectionError,
    )


def test_failure_does_not_create_fallback_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure produces no fabricated platform status."""

    class FailingClient(FakeMCPClient):
        error = RuntimeError("simulated MCP failure")

    with pytest.raises(MCPIntegrationError):
        run_tool_with_fake_client(
            monkeypatch,
            FailingClient,
        )


def test_adk_agent_remains_constructible_after_mcp_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MCP failure does not prevent ADK agent construction."""

    class FailingClient(FakeMCPClient):
        error = RuntimeError("simulated MCP failure")

    with pytest.raises(MCPIntegrationError):
        run_tool_with_fake_client(
            monkeypatch,
            FailingClient,
        )

    agent = create_mcp_enabled_agent()

    assert agent.name == "enterprise_mcp_agent"
    assert len(agent.tools) == 1


def test_failure_exception_is_runtime_error() -> None:
    """MCPIntegrationError remains compatible with runtime failures."""
    assert issubclass(
        MCPIntegrationError,
        RuntimeError,
    )
