# ============================================================================
# Physical AI Robot — Backend image
# Multi-stage: build wheels once, run on a slim runtime as a non-root user.
# ============================================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System libs required by OpenCV (headless still needs libGL/glib stubs) + psql client for healthchecks.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Dependency layer (cached unless requirements change) ---
COPY requirements.txt ./
RUN pip install -r requirements.txt

# --- Application code ---
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

# Non-root runtime user.
RUN useradd --create-home --uid 10001 robot \
    && mkdir -p /app/models \
    && chown -R robot:robot /app
USER robot

EXPOSE 8000

# Container-level liveness probe hitting the health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Default command runs the API. Migrations are applied by the entrypoint in
# docker-compose (alembic upgrade head) before the server starts.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
