"""HTTP request correlation helpers."""

from uuid import uuid4

from fastapi import Request


def get_request_id(request: Request) -> str:
    """Return the existing request ID or create one."""
    request_id = request.headers.get("X-Request-ID")

    if isinstance(request_id, str):
        return request_id

    return str(uuid4())
