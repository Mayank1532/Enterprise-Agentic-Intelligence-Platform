"""Deterministic ADK tool lifecycle policy."""

from google.adk.tools.tool_context import ToolContext

from enterprise_ai.core.callback import (
    CallbackAction,
    CallbackDecision,
)


class ToolLifecyclePolicy:
    """Apply deterministic policy at tool lifecycle boundaries."""

    def before_tool(
        self,
        tool_context: ToolContext,
    ) -> CallbackDecision:
        """Validate the tool invocation context."""
        session = tool_context.session

        if session is None or not session.id:
            return CallbackDecision(
                action=CallbackAction.ABSTAIN,
                reason="tool session identity is unavailable",
            )

        return CallbackDecision(
            action=CallbackAction.CONTINUE,
            reason="tool session identity is available",
        )

    def after_tool(
        self,
        tool_context: ToolContext,
    ) -> CallbackDecision:
        """Produce a deterministic completion decision."""
        return CallbackDecision(
            action=CallbackAction.CONTINUE,
            reason="tool lifecycle completed",
        )


def create_tool_lifecycle_policy() -> ToolLifecyclePolicy:
    """Create the deterministic tool lifecycle policy."""
    return ToolLifecyclePolicy()
