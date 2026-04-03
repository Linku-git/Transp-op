#!/bin/bash
set -e

# Redis is optional — background task queuing is disabled if unavailable
redis-server --daemonize yes --logfile /tmp/redis.log 2>/dev/null \
  || echo "WARNING: Redis not available — background tasks disabled"

# Build DATABASE_URL for asyncpg from Replit-provided PostgreSQL env vars
if [ -n "$PGHOST" ]; then
  export DATABASE_URL="postgresql+asyncpg://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE}"
  export DATABASE_URL_SYNC="postgresql+psycopg2://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE}"
else
  RAW_URL="${DATABASE_URL:-postgresql://postgres:password@helium/heliumdb}"
  export DATABASE_URL="${RAW_URL/postgresql:\/\//postgresql+asyncpg://}"
  export DATABASE_URL_SYNC="${RAW_URL/postgresql:\/\//postgresql+psycopg2://}"
fi

export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="production"
export DEBUG="false"
export LOG_LEVEL="INFO"
export SECRET_KEY="${SECRET_KEY:-transpop-prod-secret-change-me}"

echo "Running database migrations..."
cd backend
python -m alembic upgrade head
echo "Migrations complete."

# Start FastAPI — serves both the API and the built React SPA on port 8000
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
