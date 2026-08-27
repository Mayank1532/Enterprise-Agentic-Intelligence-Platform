"""A2A AgentExecutor boundary for the Enterprise Intelligence Agent."""

from a2a.server.agent_execution import (
    AgentExecutor,
    RequestContext,
)
from a2a.server.events import EventQueue
from a2a.types import Message, Part, Role


class EnterpriseA2AExecutor(AgentExecutor):
    """Expose the platform's deterministic A2A execution boundary."""

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute one A2A message request.

        The current platform does not yet expose a production LLM
        invocation service. Therefore this boundary deliberately
        returns an explicit deterministic acknowledgement rather
        than fabricating an intelligence response.
        """
        message = context.message

        if message is None:
            raise ValueError("A2A request message is required.")

        user_input = context.get_user_input()

        if user_input:
            response_text = (
                "A2A request received successfully. "
                f"Input length: {len(user_input)} characters. "
                "The Enterprise Intelligence execution boundary "
                "is available, but agent reasoning is not yet "
                "connected to this protocol boundary."
            )
        else:
            response_text = (
                "A2A request received successfully. "
                "The Enterprise Intelligence execution boundary "
                "is available, but agent reasoning is not yet "
                "connected to this protocol boundary."
            )

        response = Message(
            message_id=message.message_id,
            context_id=context.context_id,
            task_id=context.task_id,
            role=Role.ROLE_AGENT,
            parts=[
                Part(
                    text=response_text,
                )
            ],
        )

        await event_queue.enqueue_event(response)

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Explicitly reject cancellation until task execution exists."""
        del context
        del event_queue
        return None
