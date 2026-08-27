"""A2A Agent Card discovery routes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from google.protobuf.json_format import MessageToDict

from enterprise_ai.a2a.agent_card import get_agent_card

router = APIRouter(
    prefix="",
    tags=["a2a"],
)


@router.get(
    "/.well-known/agent-card.json",
    summary="Get A2A Agent Card",
)
def agent_card() -> JSONResponse:
    """Return the A2A Agent Card used for agent discovery."""

    card = get_agent_card()

    payload = MessageToDict(
        card,
        preserving_proto_field_name=False,
    )

    return JSONResponse(content=payload)
