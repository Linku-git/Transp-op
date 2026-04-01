# Session 02 — Backend FastAPI Skeleton

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-01|Session 01]]

> Previous: [[sessions/session-01|Session 01]] | Next: [[sessions/session-03|Session 03]]

## Complexity: Medium

## Objective
Create the FastAPI application skeleton with database connection, SQLAlchemy base model, Alembic migrations, health endpoint, and basic project configuration.

---

## Tasks

- [x] Create `backend/app/main.py` — FastAPI app with CORS, lifespan events, root endpoint
- [x] Create `backend/app/config.py` — Pydantic Settings class loading from `.env`
- [x] Create `backend/app/database.py` — SQLAlchemy async engine, session factory, Base model
- [x] Create `backend/app/models/__init__.py` — Import all models
- [x] Create `backend/app/models/base.py` — Base model with id (UUID), created_at, updated_at
- [x] Create `backend/app/schemas/__init__.py`
- [x] Create `backend/app/api/__init__.py`
- [x] Create `backend/app/api/v1/__init__.py` — APIRouter with `/api/v1` prefix
- [x] Create `backend/app/api/v1/health.py` — Health check endpoint (DB, Redis connectivity)
- [x] Set up Alembic: `alembic init alembic`, configure `alembic.ini` and `env.py`
- [x] Create initial migration (empty — just verify Alembic works)
- [x] Create `backend/app/services/__init__.py`
- [x] Create `backend/app/middleware/__init__.py`
- [x] Create `backend/app/tasks/__init__.py`
- [x] Create `backend/app/utils/__init__.py`
- [x] Create `backend/tests/conftest.py` — Test database fixture, test client
- [x] Create `backend/tests/test_health.py` — Test health endpoint
- [x] Verify `GET /` returns welcome message
- [x] Verify `GET /health` returns `{"status": "healthy", "db": true, "redis": true}`
- [x] Verify `GET /docs` shows Swagger UI

## Files to Create
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/models/__init__.py`
- `backend/app/models/base.py`
- `backend/app/schemas/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/health.py`
- `backend/app/services/__init__.py`
- `backend/app/middleware/__init__.py`
- `backend/app/tasks/__init__.py`
- `backend/app/utils/__init__.py`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/tests/conftest.py`
- `backend/tests/test_health.py`

## Tests
- [x] `test_root_endpoint` — GET `/` returns 200 with welcome message
- [x] `test_health_endpoint` — GET `/api/v1/health` returns 200 with status healthy
- [x] `test_docs_accessible` — GET `/docs` returns 200
- [x] `test_openapi_schema` — GET `/openapi.json` returns valid schema with health path

## Test Results
- Tests written: 4
- Tests passing: 4
- Tests failing: 0
- Coverage: N/A (no coverage tool configured yet)

## Notes
- Alembic `env.py` configured with `include_object` filter to exclude PostGIS tiger geocoder tables from autogenerate
- Health endpoint checks both DB (SELECT 1) and Redis (PING), returns "degraded" if either fails
- `pytest.ini` uses `asyncio_mode = auto` for async test support
- Base model provides UUID primary key + `created_at`/`updated_at` timestamps via `TimestampMixin`

## Acceptance Criteria
- FastAPI app starts with `uvicorn app.main:app --reload`
- Health endpoint confirms DB and Redis connectivity
- Swagger docs accessible at `/docs`
- Alembic migrations run without errors
- All 4 tests pass

## Related Documentation
- [[DATABASE_SCHEMA]] — Database schema
- [[API_ENDPOINTS]] — API endpoints
- [[ARCHITECTURE]] — System architecture
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
