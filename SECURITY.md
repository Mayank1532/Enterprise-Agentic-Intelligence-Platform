# Security Policy

## Current API Controls

The API boundary provides:

- Configurable API-key authentication
- Public health/readiness probes
- Process-local fixed-window rate limiting
- Typed environment configuration
- Input validation through project contracts
- Safe unexpected-error handling
- Request correlation with `X-Request-ID`

## Authentication

Local development defaults to disabled authentication:

```text
API_AUTH_ENABLED=false
```

Protected deployments can enable:

```text
API_AUTH_ENABLED=true
API_AUTH_KEY=<secret>
```

If authentication is enabled without a key, the application fails safely with a configuration error rather than operating as an apparently protected service.

## Secrets

Never commit API keys, tokens, passwords, certificates, or provider credentials.

Use environment variables or a deployment secret-management facility. Real `.env` files must remain outside version control.

## Rate Limiting

The current limiter is process-local and fixed-window. It is intentionally not presented as a distributed production limiter.

For horizontally scaled deployments, use a shared gateway or external rate-limit store.

## Health Endpoints

`/health` and `/ready` remain unauthenticated so infrastructure can probe the service. Health responses must not contain secrets or sensitive operational data.

## Portfolio Security Ownership

FORTRESS-MCP owns advanced zero-trust MCP controls such as authentication/authorization, policy evaluation, tool permissions, risk/confirmation controls, prompt-injection defenses, and audit/security boundaries.

This project implements only the API-boundary controls appropriate to its scope rather than duplicating that dedicated security gateway.

## Reporting

Do not publish credentials, tokens, personal information, or exploit details in public issues. Report suspected security problems privately to the project maintainer.
