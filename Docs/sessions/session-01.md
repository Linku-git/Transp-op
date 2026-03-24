# Session 01 — Monorepo Setup & Docker Environment

## Phase: 0 — Cadrage & Setup
## Prerequisites: None

> Next: [[sessions/session-02|Session 02]]

## Complexity: Medium

## Objective
Set up the project monorepo structure, Docker Compose development environment with PostgreSQL+PostGIS, Redis, and OSRM routing engine.

---

## Tasks

- [ ] Create root project directory structure (`backend/`, `frontend/`, `mobile/`, `Docs/`)
- [ ] Create `backend/` skeleton with `app/` directory and `__init__.py` files
- [ ] Create `backend/requirements.txt` with initial dependencies (fastapi, uvicorn, sqlalchemy, geoalchemy2, psycopg2-binary, alembic, redis, celery, pydantic, python-dotenv)
- [ ] Create `backend/Dockerfile` (Python 3.11 slim, install requirements, expose 8000)
- [ ] Create `backend/.env.example` with all environment variables
- [ ] Create `frontend/` scaffold placeholder (package.json minimal)
- [ ] Create `docker-compose.yml` with services:
  - `db`: PostgreSQL 15 + PostGIS (port 5432, volume for data persistence)
  - `redis`: Redis 7 (port 6379)
  - `osrm`: OSRM backend with pre-loaded Morocco/France map data (port 5000)
  - `backend`: FastAPI app (port 8000, volume mount for live reload)
- [ ] Create `.env` file with default development values
- [ ] Create `.gitignore` (Python, Node, Flutter, IDE files, .env, __pycache__)
- [ ] Create `README.md` at root with quick start instructions
- [ ] Verify `docker-compose up -d` starts all services
- [ ] Verify PostgreSQL is accessible and PostGIS extension loads (`CREATE EXTENSION postgis;`)
- [ ] Verify Redis is accessible (`redis-cli ping`)

## Files to Create
- `docker-compose.yml`
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/app/__init__.py`
- `.env`
- `.gitignore`

## Tests
- [ ] `docker-compose up -d` completes without errors
- [ ] `docker-compose exec db psql -U transpop -c "SELECT PostGIS_Version();"` returns version
- [ ] `docker-compose exec redis redis-cli ping` returns PONG
- [ ] All containers stay healthy for 60 seconds

## Acceptance Criteria
- All Docker services start and stay running
- PostgreSQL has PostGIS extension enabled
- Redis is accessible
- Backend container builds successfully
- Project structure matches the conventions in `agents.md`

## Related Documentation
- [[ARCHITECTURE]] — System architecture
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
