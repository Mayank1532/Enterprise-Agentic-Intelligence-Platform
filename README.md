# Enterprise Agentic Intelligence Platform

Provider-neutral, evidence-first enterprise agentic intelligence platform.

## Current Release

- Phase: 10A — Production API Security Boundary
- Commit: `c626f6d`
- Branch: `main`
- Validation: 561 tests passed; Ruff passed; Mypy passed
- CI: Green
- Working tree: clean and synchronized with `origin/main`

## Objective

A production-style enterprise GenAI platform demonstrating deterministic evidence handling, retrieval, live data, grounding, evaluation, agent interoperability, MCP integration, reliability, observability, and production hardening.

## Capabilities

- Evidence-first retrieval and metadata filtering
- Deterministic local retrieval, BM25, embeddings, and reranking
- Live external data representation
- Grounding and unsupported-claim detection
- Evaluation and regression testing
- MCP integration
- A2A discovery and communication
- Ingestion observability and failure recovery
- FastAPI health/readiness endpoints
- Request correlation with `X-Request-ID`
- Configurable API-key authentication
- Configurable process-local rate limiting
- Docker packaging
- GitHub Actions CI
- pytest, Ruff, and Mypy quality gates

## Architecture

```text
Client
  |
  v
FastAPI API Boundary
  |
  +--> Authentication / Rate Limiting
  |
  +--> A2A
  |
  +--> Agent / Orchestration
          |
          +--> Retrieval / Evidence
          +--> Grounding / Evaluation
          +--> MCP Tool Boundary
          +--> Live Data
          +--> Recovery / Observability
```

Advanced security and recovery responsibilities are intentionally separated across the portfolio. Full zero-trust tool authorization and prompt-injection defenses belong to FORTRESS-MCP; advanced retry, checkpointing, circuit-breaker, fallback, and recovery observability belong to RECOVER-AI.

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic / pydantic-settings
- A2A SDK
- MCP
- Google ADK
- Uvicorn
- uv
- Docker
- GitHub Actions
- pytest
- Ruff
- Mypy

## Setup

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn enterprise_ai.api.app:app --reload
```

Default API address:

```text
http://127.0.0.1:8000
```

## Health Checks

```text
GET /health
GET /ready
```

These endpoints remain public for orchestration and load-balancer probes.

## API Security

Authentication is configurable:

```text
API_AUTH_ENABLED=false
API_AUTH_KEY=
```

When enabled, protected requests require:

```text
X-API-Key: <configured-key>
```

Rate limiting:

```text
API_RATE_LIMIT_REQUESTS=60
API_RATE_LIMIT_WINDOW_SECONDS=60
```

The current limiter is process-local by design. Distributed rate limiting is deferred until the deployment architecture requires it.

## Testing

```powershell
uv run pytest -q
uv run ruff check .
uv run mypy src
```

Validated baseline:

```text
561 passed
Ruff: PASS
Mypy: PASS
GitHub Actions: GREEN
```

## Docker

```powershell
docker build -t enterprise-agentic-intelligence-platform .
docker run --rm -p 8000:8000 enterprise-agentic-intelligence-platform
```

Verify `/health` and `/ready` after startup.

## CI/CD

GitHub Actions validates dependency installation, Ruff, Mypy, and pytest. The main branch is expected to remain green.

## Engineering Rules

- Prefer deterministic logic where an LLM is unnecessary.
- Treat model-generated data as untrusted input.
- Preserve evidence and source metadata.
- Prefer abstention over unsupported factual claims.
- Mock expensive external components in normal unit tests.
- Keep integration tests focused and reproducible.
- Reuse proven portfolio infrastructure where appropriate.
- Reject unnecessary technology and scope creep.
- Commit at meaningful milestones.
- Document real failures and their prevention.

## Scope Boundaries

This project does not attempt to become a universal security or distributed-reliability framework.

Deferred/separately owned capabilities include full RBAC/policy engines, advanced prompt-injection defenses, enterprise data-access policy enforcement, distributed rate limiting, full OpenTelemetry deployment, and circuit-breaker/recovery frameworks.

## License

Portfolio/reference engineering project.
