"""FastAPI application entry point."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from a2a.server.request_handlers import DefaultRequestHandlerV2
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from enterprise_ai.a2a.agent_card import get_agent_card
from enterprise_ai.a2a.discovery import router as a2a_router
from enterprise_ai.a2a.executor import EnterpriseA2AExecutor
from enterprise_ai.config.settings import get_settings
from enterprise_ai.core.errors import APIError
from enterprise_ai.core.health import HealthResponse, ReadinessResponse
from enterprise_ai.logging.setup import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and release application resources."""
    logger.info("Starting %s", settings.app_name)
    yield
    logger.info("Stopping %s", settings.app_name)



app = FastAPI(
    title="Enterprise Agentic Intelligence Platform",
    description="Provider-neutral, evidence-first Agentic AI platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(a2a_router)

_a2a_handler = DefaultRequestHandlerV2(
    agent_executor=EnterpriseA2AExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=get_agent_card(),
)

_a2a_jsonrpc_routes = create_jsonrpc_routes(
    _a2a_handler,
    rpc_url="/a2a",
)

add_a2a_routes_to_fastapi(
    app,
    jsonrpc_routes=_a2a_jsonrpc_routes,
)


@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach a correlation ID to every response."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())

    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    _: Exception,
) -> JSONResponse:
    """Return a safe error response for unexpected failures."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.exception(
        "Unhandled application error | request_id=%s",
        request_id,
    )

    error = APIError(
        code="INTERNAL_ERROR",
        message="An internal error occurred.",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=500,
        content=error.model_dump(),
        headers={"X-Request-ID": request_id},
    )


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Return application health."""
    return HealthResponse(
        service=settings.app_name,
        status="ok",
        environment=settings.app_env,
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["system"])
def readiness() -> ReadinessResponse:
    """Return application readiness."""
    return ReadinessResponse(
        service=settings.app_name,
        status="ready",
        environment=settings.app_env,
    )

