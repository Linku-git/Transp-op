#!/bin/bash
# Start Redis in background
redis-server --daemonize yes --logfile /tmp/redis.log

# Override DATABASE_URL to use asyncpg for async SQLAlchemy
export DATABASE_URL="postgresql+asyncpg://postgres:password@helium:5432/heliumdb"
export DATABASE_URL_SYNC="postgresql+psycopg2://postgres:password@helium:5432/heliumdb"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="replit-dev-secret-change-me-in-production"
export ENVIRONMENT="development"
export DEBUG="true"
export LOG_LEVEL="INFO"

# Start Backend API (no --reload to ensure fast port binding)
cd backend
exec uvicorn app.main:app --host localhost --port 8000
