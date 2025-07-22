import psycopg2
from app.config import settings
psycopg2.connect(settings.DATABASE_URL.replace(\"postgresql+psycopg2://\", \"postgresql://\"))' 2>/dev/null; do echo 'Database not ready, waiting...'; sleep 2; done && echo 'Running migrations...' && uv run alembic upgrade head && echo 'Creating mock data...' && uv run python dev/upload_mock_data.py && echo 'Starting app...' && exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
]
