"""Minimal Google ADK agent foundation."""

from google.adk.agents import Agent


def create_foundation_agent() -> Agent:
    """Create the Phase 3 foundation agent."""
    return Agent(
        name="enterprise_foundation_agent",
        description=("Foundation agent for the Enterprise Agentic Intelligence Platform."),
        instruction=(
            "You are the foundation agent of the Enterprise "
            "Agentic Intelligence Platform. "
            "Do not invent evidence. "
            "Do not claim access to tools that have not been provided."
        ),
    )
