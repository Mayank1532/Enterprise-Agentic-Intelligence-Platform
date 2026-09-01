# Changelog

## Phase 10A — 2026-09-01

### Added

- Configurable API-key authentication.
- Process-local fixed-window API rate limiting.
- `X-API-Key` protection for non-health/readiness API requests.
- `Retry-After` response for rate-limit rejection.
- Security unit tests.

### Validation

- 561 tests passed.
- Ruff passed.
- Mypy passed.
- GitHub Actions passed.
- Local `main` synchronized with `origin/main`.

### Release Commit

`c626f6d feat: add API security controls`

## Phase 9

- Completed ingestion observability and failure-recovery work.
- Established the production-hardening baseline used by Phase 10.
