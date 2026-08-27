"""Tests for the A2A AgentExecutor boundary."""

import pytest
from a2a.server.agent_execution import RequestContext
from a2a.server.context import ServerCallContext
from a2a.server.events import EventQueue
from a2a.types import (
    Message,
    Part,
    Role,
    SendMessageRequest,
)

from enterprise_ai.a2a.executor import EnterpriseA2AExecutor


class RecordingEventQueue(EventQueue):
    """Event queue test double that records emitted events."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[object] = []

    async def enqueue_event(self, event: object) -> None:
        self.events.append(event)


def build_context(user_input: str) -> RequestContext:
    """Build a minimal SDK-compatible request context."""
    message = Message(
        message_id="test-message-id",
        context_id="test-context-id",
        task_id="test-task-id",
        role=Role.ROLE_USER,
        parts=[
            Part(
                text=user_input,
            )
        ],
    )

    request = SendMessageRequest(
        message=message,
    )

    call_context = ServerCallContext()

    return RequestContext(
        call_context=call_context,
        request=request,
        task_id="test-task-id",
        context_id="test-context-id",
    )


@pytest.mark.anyio
async def test_executor_emits_agent_message() -> None:
    """Executor emits exactly one agent response message."""
    executor = EnterpriseA2AExecutor()
    queue = RecordingEventQueue()
    context = build_context("Hello A2A")

    await executor.execute(context, queue)

    assert len(queue.events) == 1

    response = queue.events[0]

    assert isinstance(response, Message)
    assert response.role == Role.ROLE_AGENT
    assert response.context_id == "test-context-id"
    assert response.task_id == "test-task-id"


@pytest.mark.anyio
async def test_executor_acknowledges_user_input() -> None:
    """Executor response records the received input length."""
    executor = EnterpriseA2AExecutor()
    queue = RecordingEventQueue()
    context = build_context("Hello A2A")

    await executor.execute(context, queue)

    response = queue.events[0]

    assert isinstance(response, Message)
    assert response.parts[0].text is not None
    assert "Input length: 9 characters." in response.parts[0].text


@pytest.mark.anyio
async def test_executor_handles_empty_input() -> None:
    """Executor emits a deterministic response for empty input."""
    executor = EnterpriseA2AExecutor()
    queue = RecordingEventQueue()
    context = build_context("")

    await executor.execute(context, queue)

    assert len(queue.events) == 1

    response = queue.events[0]

    assert isinstance(response, Message)
    assert response.role == Role.ROLE_AGENT
    assert response.parts[0].text is not None
    assert "A2A request received successfully." in response.parts[0].text


@pytest.mark.anyio
async def test_executor_rejects_missing_message() -> None:
    """Executor rejects a request context without a message."""
    call_context = ServerCallContext()

    context = RequestContext(
        call_context=call_context,
        request=None,
        task_id="test-task-id",
        context_id="test-context-id",
    )

    executor = EnterpriseA2AExecutor()
    queue = RecordingEventQueue()

    with pytest.raises(ValueError, match="A2A request message is required"):
        await executor.execute(context, queue)


@pytest.mark.anyio
async def test_executor_cancel_is_explicit_noop() -> None:
    """Cancellation is explicitly implemented until task execution exists."""
    executor = EnterpriseA2AExecutor()
    queue = RecordingEventQueue()
    context = build_context("Hello A2A")

    result = await executor.cancel(context, queue)

    assert result is None
    assert queue.events == []
