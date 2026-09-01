# Contributing

## Requirements

- Python 3.12
- uv
- Git

## Setup

```powershell
uv sync
```

## Development Workflow

```text
edit -> test -> lint/type-check -> git status
     -> git add specific files -> commit -> push -> verify remote
```

Do not commit generated caches, virtual environments, local secrets, or temporary experiments.

## Quality Gates

```powershell
uv run pytest -q
uv run ruff check .
uv run mypy src
git diff --check
```

All checks should pass before committing.

## Testing Principles

- Keep unit tests deterministic and fast.
- Mock external providers where appropriate.
- Cover important integration boundaries.
- Add regression tests for new behavior.
- Keep the complete test suite green.

## Scope Control

Do not add dependencies or frameworks merely for checklist value. A change should solve a real requirement, improve technical/learning value, and fit the project timebox.

Avoid unrelated refactoring and cosmetic architecture changes.

## Commits

Prefer focused milestone commits, for example:

```text
feat: add API security controls
test: add grounding regression cases
docs: finalize release documentation
```

Before pushing, verify the intended files are staged and the remote branch is synchronized afterward.
