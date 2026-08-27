"""Tests for A2A Agent Card and discovery."""

from fastapi.testclient import TestClient

from enterprise_ai.a2a.agent_card import (
    A2A_PROTOCOL_VERSION,
    build_agent_card,
)
from enterprise_ai.api.app import app


def test_agent_card_contains_required_identity() -> None:
    """Agent Card exposes stable agent identity metadata."""

    card = build_agent_card()

    assert card.name == "Enterprise Intelligence Agent"
    assert card.description
    assert card.version == "0.1.0"


def test_agent_card_contains_protocol_interface() -> None:
    """Agent Card declares an A2A 1.0 interface."""

    card = build_agent_card()

    assert len(card.supported_interfaces) == 1

    interface = card.supported_interfaces[0]

    assert interface.url == "http://localhost:8000/a2a"
    assert interface.protocol_binding == "HTTP+JSON"
    assert interface.protocol_version == A2A_PROTOCOL_VERSION


def test_agent_card_contains_capabilities() -> None:
    """Agent Card exposes explicit capabilities."""

    card = build_agent_card()

    assert card.capabilities.streaming is False
    assert card.capabilities.push_notifications is False
    assert card.capabilities.extended_agent_card is False


def test_agent_card_contains_skill() -> None:
    """Agent Card exposes the platform skill."""

    card = build_agent_card()

    assert len(card.skills) == 1

    skill = card.skills[0]

    assert skill.id == "enterprise-intelligence"
    assert skill.name == "Enterprise Intelligence"
    assert skill.description
    assert "enterprise-ai" in skill.tags


def test_agent_card_discovery_endpoint() -> None:
    """The standard A2A Agent Card discovery endpoint is available."""

    with TestClient(app) as client:
        response = client.get("/.well-known/agent-card.json")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "Enterprise Intelligence Agent"
    assert payload["version"] == "0.1.0"
    assert payload["supportedInterfaces"][0]["protocolVersion"] == "1.0"
    assert payload["skills"][0]["id"] == "enterprise-intelligence"
