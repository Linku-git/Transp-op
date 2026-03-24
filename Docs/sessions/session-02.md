# Session 02 — Backend FastAPI Skeleton

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-01|Session 01]]

> Previous: [[sessions/session-01|Session 01]] | Next: [[sessions/session-03|Session 03]]

## Complexity: Medium

## Objective
Create the FastAPI application skeleton with database connection, SQLAlchemy base model, Alembic migrations, health endpoint, and basic project configuration.

---

## Tasks

- [ ] Create `backend/app/main.py` — FastAPI app with CORS, lifespan events, root endpoint
- [ ] Create `backend/app/config.py` — Pydantic Settings class loading from `.env`
- [ ] Create `backend/app/database.py` — SQLAlchemy async engine, session factory, Base model
- [ ] Create `backend/app/models/__init__.py` — Import all models
- [ ] Create `backend/app/models/base.py` — Base model with id (UUID), created_at, updated_at
- [ ] Create `backend/app/schemas/__init__.py`
- [ ] Create `backend/app/api/__init__.py`
- [ ] Create `backend/app/api/v1/__init__.py` — APIRouter with `/api/v1` prefix
- [ ] Create `backend/app/api/v1/health.py` — Health check endpoint (DB, Redis connectivity)
- [ ] Set up Alembic: `alembic init alembic`, configure `alembic.ini` and `env.py`
- [ ] Create initial migration (empty — just verify Alembic works)
- [ ] Create `backend/app/services/__init__.py`
- [ ] Create `backend/app/middleware/__init__.py`
- [ ] Create `backend/app/tasks/__init__.py`
- [ ] Create `backend/app/utils/__init__.py`
- [ ] Create `backend/tests/conftest.py` — Test database fixture, test client
- [ ] Create `backend/tests/test_health.py` — Test health endpoint
- [ ] Verify `GET /` returns welcome message
- [ ] Verify `GET /health` returns `{"status": "healthy", "db": true, "redis": true}`
- [ ] Verify `GET /docs` shows Swagger UI

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
- [ ] `test_root_endpoint` — GET `/` returns 200 with welcome message
- [ ] `test_health_endpoint` — GET `/health` returns 200 with status healthy
- [ ] `test_docs_accessible` — GET `/docs` returns 200
- [ ] `test_database_connection` — SQLAlchemy can connect and execute query

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
