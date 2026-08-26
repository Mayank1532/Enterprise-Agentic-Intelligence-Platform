"""Tests for deterministic MCP prompts."""

import asyncio

from enterprise_ai.mcp.prompts import (
    PLATFORM_ANALYSIS_PROMPT_NAME,
    render_platform_analysis_prompt,
)
from enterprise_ai.mcp.server import (
    create_mcp_server,
    mcp_server,
)

EXPECTED_TOPIC = "MCP architecture"

EXPECTED_PROMPT = (
    "Analyze the following Enterprise AI platform topic using "
    "evidence-first reasoning:\n\n"
    "Topic: MCP architecture\n\n"
    "Requirements:\n"
    "- distinguish facts from assumptions\n"
    "- identify supporting evidence\n"
    "- identify uncertainty explicitly\n"
    "- do not invent unavailable information"
)


def test_platform_analysis_prompt_is_deterministic() -> None:
    """Prompt rendering is deterministic."""
    first = render_platform_analysis_prompt(EXPECTED_TOPIC)
    second = render_platform_analysis_prompt(EXPECTED_TOPIC)

    assert first == second


def test_platform_analysis_prompt_contract() -> None:
    """Prompt rendering produces the canonical content."""
    assert render_platform_analysis_prompt(EXPECTED_TOPIC) == EXPECTED_PROMPT


def test_platform_analysis_prompt_rejects_empty_topic() -> None:
    """Empty topics are rejected explicitly."""
    try:
        render_platform_analysis_prompt("   ")
    except ValueError as exc:
        assert str(exc) == "topic must not be empty"
    else:
        raise AssertionError("Expected ValueError for empty topic.")


def test_platform_analysis_prompt_name_is_canonical() -> None:
    """Prompt uses the canonical MCP name."""
    assert PLATFORM_ANALYSIS_PROMPT_NAME == "platform_analysis"


def test_mcp_server_can_be_created_with_prompt() -> None:
    """Server can be created with the registered prompt."""
    server = create_mcp_server()

    assert server is not None


def test_global_mcp_server_is_available() -> None:
    """Configured MCP server remains available."""
    assert mcp_server is not None


def test_mcp_prompt_protocol_rendering() -> None:
    """The MCP get_prompt path renders the registered prompt."""

    async def run() -> None:
        result = await mcp_server.get_prompt(
            PLATFORM_ANALYSIS_PROMPT_NAME,
            {"topic": EXPECTED_TOPIC},
        )

        assert result.description == (
            "Create an evidence-first analysis request for a platform topic."
        )
        assert len(result.messages) == 1
        assert result.messages[0].role == "user"
        assert result.messages[0].content.type == "text"
        assert result.messages[0].content.text == EXPECTED_PROMPT

    asyncio.run(run())


def test_mcp_prompt_protocol_rejects_missing_required_argument() -> None:
    """Missing required prompt arguments fail deterministically."""

    async def run() -> None:
        try:
            await mcp_server.get_prompt(
                PLATFORM_ANALYSIS_PROMPT_NAME,
                {},
            )
        except (TypeError, ValueError) as exc:
            assert "topic" in str(exc).lower()
        else:
            raise AssertionError("Expected prompt rendering to reject missing topic.")

    asyncio.run(run())
