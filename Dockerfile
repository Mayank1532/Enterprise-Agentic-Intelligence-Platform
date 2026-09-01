FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv==0.11.28 \
    && uv sync --locked --no-dev

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "enterprise_ai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
