"""HTTP-level tests for the A2A JSON-RPC endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from enterprise_ai.api.app import app


@pytest.mark.anyio
async def test_a2a_jsonrpc_endpoint_accepts_message() -> None:
    """A2A V1.0 JSON-RPC endpoint accepts a SendMessage request."""
    payload = {
        "jsonrpc": "2.0",
        "id": "test-request-1",
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": "test-message-1",
                "contextId": "test-context-1",
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": "Hello A2A",
                    }
                ],
            }
        },
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/a2a",
            headers={
                "A2A-Version": "1.0",
            },
            json=payload,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "test-request-1"
    assert "result" in body


@pytest.mark.anyio
async def test_a2a_endpoint_rejects_unknown_path() -> None:
    """Unknown A2A paths are not silently accepted."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/a2a/unknown",
            json={},
        )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_a2a_endpoint_rejects_unknown_method() -> None:
    """Unknown JSON-RPC methods return a protocol error."""
    payload = {
        "jsonrpc": "2.0",
        "id": "test-request-unknown",
        "method": "UnknownMethod",
        "params": {},
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/a2a",
            headers={
                "A2A-Version": "1.0",
            },
            json=payload,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "test-request-unknown"
    assert "error" in body
