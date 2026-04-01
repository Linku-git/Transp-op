# Transpop — Changelog

> All notable changes to this project are documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
> See also: [[PROGRESS]] | [[ROADMAP]]

---

## [Session-02] — 2026-04-01
### Added
- `backend/app/config.py` — Pydantic Settings loading from `.env`
- `backend/app/database.py` — SQLAlchemy async engine, session factory, `get_db` dependency
- `backend/app/models/base.py` — `BaseModel` with UUID pk + `TimestampMixin` (created_at, updated_at)
- `backend/app/api/v1/health.py` — Health endpoint checking DB and Redis connectivity
- `backend/app/api/v1/__init__.py` — API v1 router aggregation
- `backend/alembic.ini` + `alembic/env.py` — Async Alembic configured with PostGIS table exclusion
- `backend/tests/conftest.py` — Async test client fixture (httpx + ASGITransport)
- `backend/tests/test_health.py` — 4 tests (root, health, docs, openapi schema)
- `backend/pytest.ini` — Pytest async mode config

### Changed
- `backend/app/main.py` — Added lifespan events, API router inclusion, config-driven settings

---

## [Session-01] — 2026-04-01
### Added
- Monorepo directory structure (`backend/`, `frontend/`, `mobile/`)
- Backend FastAPI skeleton with `app/` package and all sub-modules (models, schemas, api, services, middleware, tasks, utils)
- `backend/requirements.txt` with all core dependencies (FastAPI, SQLAlchemy, GeoAlchemy2, Celery, OR-Tools, scikit-learn)
- `backend/Dockerfile` (Python 3.11 slim with PostGIS system dependencies)
- `backend/.env.example` with all environment variables
- `docker-compose.yml` with 4 services: PostgreSQL 15 + PostGIS 3.4, Redis 7, OSRM, FastAPI backend
- `.env` with default development values
- `frontend/package.json` placeholder scaffold
- Root `README.md` with quick start instructions and access URLs
- Minimal FastAPI app with `/` and `/health` endpoints

---

## [Session-00] — 2026-03-24
### Added
- Claude Code configuration (`.claude/` directory with settings, rules, agents, skills)
- `CLAUDE.md` root context file with `@import` directives
- Obsidian vault enhancements (`INDEX.md`, `CHANGELOG.md`, ADR template)
- `.gitignore` for Python, Node, Flutter, IDE, and secrets
- Git repository initialized
