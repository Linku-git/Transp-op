#!/bin/bash
set -e

# Start Redis in background
redis-server --daemonize yes --logfile /tmp/redis.log

# Build the DATABASE_URL for asyncpg from the Replit-provided PostgreSQL env vars
# PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE are set automatically by Replit
if [ -n "$PGHOST" ]; then
  export DATABASE_URL="postgresql+asyncpg://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE}"
  export DATABASE_URL_SYNC="postgresql+psycopg2://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE}"
else
  # Fallback: rewrite the scheme from the provided DATABASE_URL
  RAW_URL="${DATABASE_URL:-postgresql://postgres:password@helium/heliumdb}"
  export DATABASE_URL="${RAW_URL/postgresql:\/\//postgresql+asyncpg://}"
  export DATABASE_URL_SYNC="${RAW_URL/postgresql:\/\//postgresql+psycopg2://}"
fi

export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="production"
export DEBUG="false"
export LOG_LEVEL="INFO"

# Use SECRET_KEY from env if set, else a default (set it as a secret for production)
export SECRET_KEY="${SECRET_KEY:-transpop-prod-secret-change-me}"

# Run Alembic migrations to ensure schema is up to date
echo "Running database migrations..."
cd backend
python -m alembic upgrade head
echo "Migrations complete."

# Start the FastAPI server (serves both API + frontend SPA)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
