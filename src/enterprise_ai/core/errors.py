"""API error contracts."""

from pydantic import BaseModel


class APIError(BaseModel):
    """Consistent API error response."""

    code: str
    message: str
    request_id: str
