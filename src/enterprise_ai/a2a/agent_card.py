"""A2A Agent Card definition and discovery metadata."""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

A2A_PROTOCOL_VERSION = "1.0"
A2A_PROTOCOL_BINDING = "HTTP+JSON"
A2A_AGENT_CARD_PATH = "/.well-known/agent-card.json"

AGENT_NAME = "Enterprise Intelligence Agent"
AGENT_DESCRIPTION = (
    "Provider-neutral evidence-first agent for the "
    "Enterprise Agentic Intelligence Platform."
)
AGENT_VERSION = "0.1.0"

AGENT_SKILL = AgentSkill(
    id="enterprise-intelligence",
    name="Enterprise Intelligence",
    description=(
        "Provides evidence-oriented enterprise intelligence "
        "capabilities through the platform."
    ),
    tags=[
        "enterprise-ai",
        "agentic-ai",
        "evidence",
        "intelligence",
    ],
    examples=[
        "Find evidence relevant to an enterprise question.",
        "Return grounded intelligence with source information.",
    ],
    input_modes=[
        "text/plain",
        "application/json",
    ],
    output_modes=[
        "text/plain",
        "application/json",
    ],
)

AGENT_CAPABILITIES = AgentCapabilities(
    streaming=False,
    push_notifications=False,
    extended_agent_card=False,
)

AGENT_INTERFACE = AgentInterface(
    url="http://localhost:8000/a2a",
    protocol_binding=A2A_PROTOCOL_BINDING,
    protocol_version=A2A_PROTOCOL_VERSION,
)


def build_agent_card() -> AgentCard:
    """Build the public A2A Agent Card."""

    return AgentCard(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        supported_interfaces=[AGENT_INTERFACE],
        version=AGENT_VERSION,
        capabilities=AGENT_CAPABILITIES,
        default_input_modes=[
            "text/plain",
            "application/json",
        ],
        default_output_modes=[
            "text/plain",
            "application/json",
        ],
        skills=[AGENT_SKILL],
    )


def get_agent_card() -> AgentCard:
    """Return the platform Agent Card."""

    return build_agent_card()
