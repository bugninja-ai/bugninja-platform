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