FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md ./

RUN pip install --no-cache-dir uv==0.11.28 \
    && uv sync --locked --no-dev

COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "enterprise_ai.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
