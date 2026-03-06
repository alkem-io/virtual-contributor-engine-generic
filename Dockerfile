# Stage 1: Build stage (Debian Python for distroless compatibility)
FROM debian:bookworm-slim AS builder

# Notes:
# - Distroless Python uses Debian 12 (bookworm). Building deps on bookworm keeps ABI compatibility.
# - Debian enforces PEP 668 for system pip; install Poetry into an isolated venv to avoid it.

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
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

# Ensure the lock metadata matches the builder Python (3.11) so exported markers are correct
RUN /poetry-venv/bin/poetry lock --no-update

# Export only runtime dependencies and install into a dedicated dir
RUN /poetry-venv/bin/poetry export --format requirements.txt --output requirements.txt --without-hashes --only main && \
    python3 -m pip install --no-cache-dir --target=/opt/python -r requirements.txt

# Copy only runtime application files
COPY ai_adapter.py config.py main.py models.py prompts.py ./

# Stage 2: Runtime stage - Google distroless Python image
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app

COPY --from=builder --chown=nonroot:nonroot /opt/python /opt/python
COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/python

USER nonroot

ENTRYPOINT ["python3", "main.py"]
