# Stage 1: Builder
# Use a slim image for building to ensure we have necessary build tools
FROM python:3.11-slim-bookworm AS builder

# Install git (required for git dependencies in pyproject.toml)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
# We install poetry in the builder stage only
RUN pip install poetry && poetry self add poetry-plugin-export

# Copy only the files needed for dependency installation first
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
# This resolves the dependency tree and creates a standard requirements file
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install dependencies into a specific directory
# --target allows us to install packages into a specific folder that we can copy later
RUN pip install --no-cache-dir --target /app/site-packages -r requirements.txt

# Stage 2: Runtime
# Use distroless image for the final stage to minimize size and attack surface
# gcr.io/distroless/python3-debian12 contains Python 3.11
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy installed dependencies from the builder stage
# We place them in the standard site-packages location for Python 3.11
COPY --from=builder /app/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code
# Note: .dockerignore ensures we don't copy unnecessary files like .git, .venv, etc.
COPY . /app

# Set PYTHONPATH to include the installed packages
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# Run the application
# Distroless images do not have a shell, so we must use the exec form (JSON array)
CMD ["main.py"]
