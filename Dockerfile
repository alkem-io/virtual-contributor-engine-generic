# Stage 1: Build stage - Python 3.12 (required by pyproject.toml)
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1

# Install Poetry into an isolated venv (builder-only)
RUN python3 -m venv /poetry-venv && \
    /poetry-venv/bin/pip install --no-cache-dir poetry==1.8.5

# Copy only dependency files first (better layer caching)
COPY pyproject.toml poetry.lock* ./

# Export only runtime dependencies and install into a dedicated dir
RUN /poetry-venv/bin/poetry export --format requirements.txt --output requirements.txt --without-hashes --only main && \
    python3 -m pip install --no-cache-dir --target=/opt/python -r requirements.txt

# Copy only runtime application files
COPY ai_adapter.py config.py main.py models.py prompts.py ./

# Stage 2: Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /opt/python /opt/python
COPY --from=builder /app /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/python

RUN useradd --create-home --uid 1000 appuser
USER appuser

ENTRYPOINT ["python3", "main.py"]
