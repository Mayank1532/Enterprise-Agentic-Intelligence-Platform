"""Deterministic ADK agent lifecycle policy."""

from google.adk.agents.callback_context import CallbackContext

from enterprise_ai.core.callback import (
    CallbackAction,
    CallbackDecision,
)


class AgentLifecyclePolicy:
    """Apply deterministic policy at agent lifecycle boundaries."""

    def before_agent(
        self,
        context: CallbackContext,
    ) -> CallbackDecision:
        """Validate the agent invocation before execution."""
        session = context.session

        if session is None:
            return CallbackDecision(
                action=CallbackAction.ABSTAIN,
                reason="agent session is unavailable",
            )

        return CallbackDecision(
            action=CallbackAction.CONTINUE,
            reason="agent session is available",
        )

    def after_agent(
        self,
        context: CallbackContext,
    ) -> CallbackDecision:
        """Produce a deterministic completion decision."""
        return CallbackDecision(
            action=CallbackAction.CONTINUE,
            reason="agent lifecycle completed",
        )


def create_agent_lifecycle_policy() -> AgentLifecyclePolicy:
    """Create the deterministic agent lifecycle policy."""
    return AgentLifecyclePolicy()
