"""API foundation tests."""

from fastapi.testclient import TestClient

from enterprise_ai.api.app import app


def test_health_endpoint() -> None:
    """Health endpoint returns a healthy response."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "X-Request-ID" in response.headers


def test_readiness_endpoint() -> None:
    """Readiness endpoint returns a ready response."""
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert "X-Request-ID" in response.headers


def test_request_id_is_preserved() -> None:
    """Client-provided request IDs are preserved."""
    client = TestClient(app)

    request_id = "test-request-123"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
