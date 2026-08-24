"""Health endpoint tests."""

from fastapi.testclient import TestClient

from enterprise_ai.api.app import app


def test_health_endpoint() -> None:
    """Health endpoint returns the expected contract."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "enterprise-agentic-intelligence-platform"
