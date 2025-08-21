# Use Python 3.11 slim image
FROM python:3.13.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv and poe
RUN pip install uv poethepoet

# Set work directory
WORKDIR /app

# Copy elements
COPY backend/pyproject.toml ./
COPY backend/alembic.ini ./
COPY backend/mypy.ini ./
COPY backend/uv.lock ./

# Install dependencies
RUN uv sync

RUN --mount=type=secret,id=GIT_TOKEN \
    GIT_TOKEN=$(cat /run/secrets/GIT_TOKEN) && \
    git config --global url."https://${GIT_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    uv add git+https://github.com/bugninja-ai/bugninja-experiment@akos/experimenting-with-browser-use

RUN uv run playwright install
RUN uv run playwright install-deps


# Copy source code
COPY backend/app ./app
COPY backend/dev ./dev
COPY backend/alembic ./alembic

# Copy and set up entrypoint script
COPY backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]