# Use Python 3.11 slim image
FROM python:3.13.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Define build args
ARG GIT_TOKEN

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

RUN git config --global url."https://${GIT_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    uv add git+https://github.com/bugninja-ai/bugninja-experiment@akos/experimenting-with-browser-use

RUN uv run playwright install
RUN uv run playwright install-deps


# Copy source code
COPY backend/app ./app
COPY backend/dev ./dev
COPY backend/alembic ./alembic

# Create necessary directories
RUN mkdir -p /app/content/run_gifs /app/content/run_he_screenshots /app/content/screenshots

# Expose port
EXPOSE 8000

# Set up the startup command
CMD ["sh", "-c", "export PYTHONPATH=/app:$PYTHONPATH && uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]