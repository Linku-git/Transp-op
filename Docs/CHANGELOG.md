# Transpop — Changelog

> All notable changes to this project are documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
> See also: [[PROGRESS]] | [[ROADMAP]]

---

## [Session-06] — 2026-04-01
### Added
- Site SQLAlchemy model with PostGIS POINT geometry column and GIST spatial index (`backend/app/models/site.py`)
- Alembic migration for site table with GeoAlchemy2 geometry support
- Pydantic schemas: SiteCreate (with lat/lng/security_profile validation), SiteUpdate, SiteResponse, SiteSummary, SiteListResponse (`backend/app/schemas/site.py`)
- 7 CRUD API endpoints: list (paginated + city/ZFE filters), get by ID, get by code, create (with PostGIS ST_MakePoint), update (geom recalc), delete, summary (`backend/app/api/v1/sites.py`)
- 13 test cases covering all CRUD operations, validation, filters, and PostGIS geometry

---

## [Session-05] — 2026-04-01
### Added
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) — backend (ruff + mypy + pytest) and frontend (eslint + tsc + vitest)
- Ruff Python linting config (`backend/ruff.toml`) with FastAPI-compatible rules
- Mypy type checking config (`backend/mypy.ini`) with pydantic + sqlalchemy plugins
- Prettier config (`frontend/.prettierrc`) for consistent formatting
- Pre-commit hooks (`.pre-commit-config.yaml`) — ruff + prettier
- Backend scripts (`backend/scripts.sh`) — lint, format, test, seed, migrate commands
- Frontend scripts: `type-check`, `format`, `format:check` in package.json

### Fixed
- 3 B904 lint violations (raise-from-err) in auth middleware and endpoints
- 5 import sorting violations auto-fixed by ruff

---

## [Session-04] — 2026-04-01
### Added
- SQLAlchemy models: Tenant, User, Role, Permission, RolePermission (`backend/app/models/auth.py`)
- Alembic migration for all auth tables
- Pydantic v2 schemas for auth requests/responses (`backend/app/schemas/auth.py`)
- JWT auth middleware with OAuth2PasswordBearer (`backend/app/middleware/auth.py`)
- RBAC `require_role()` dependency factory (`backend/app/middleware/rbac.py`)
- Auth endpoints: POST login, POST logout, POST refresh, GET me (`backend/app/api/v1/auth.py`)
- User CRUD endpoints: GET list, POST create, PUT update, DELETE deactivate (`backend/app/api/v1/users.py`)
- Role CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/roles.py`)
- Tenant CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/tenants.py`)
- Password hashing (bcrypt) and JWT encode/decode utilities (`backend/app/utils/security.py`)
- Seed data script: default tenant, 5 system roles, admin user (`backend/app/scripts/seed_data.py`)
- 11 new tests: auth flow (8) + user management (3)

### Changed
- `backend/app/database.py` — `get_db` uses `session.begin()` context, NullPool in test mode
- `backend/requirements.txt` — added bcrypt==4.2.1, pydantic[email]

---

## [Session-03] — 2026-04-01
### Added
- Vite React TypeScript project with strict mode
- TailwindCSS v4 with full design system tokens (`@theme` block in index.css)
- Layout shell: `AppLayout`, `Sidebar` (NavLink-based navigation), `Header` (language toggle, user display)
- 7 base UI components: `Button` (4 variants), `Input`, `Card`, `DataTable` (generic typed), `Modal`, `Toast`, `Skeleton`
- Routing with lazy-loaded pages (`routes.tsx` using `createBrowserRouter`)
- Zustand auth store (`useAuthStore`) with localStorage persistence
- Axios API client with JWT interceptors
- i18n configuration (French default, English fallback) with translation stubs
- Placeholder pages: `DashboardPage`, `LoginPage`
- `frontend/Dockerfile` (multi-stage Node 18 build + nginx serve)
- Vitest test setup with jsdom + React Testing Library
- 8 tests: AppLayout render, Button variants/loading/disabled, Card render, routing navigation

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
