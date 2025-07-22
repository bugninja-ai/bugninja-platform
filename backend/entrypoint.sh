#!/bin/bash
set -e

# Set Python path to include the current directory
export PYTHONPATH=/app:$PYTHONPATH

echo "Running database migrations..."
uv run alembic upgrade head

echo "Creating mock data..."
uv run python dev/upload_mock_data.py

echo "Starting the application..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 