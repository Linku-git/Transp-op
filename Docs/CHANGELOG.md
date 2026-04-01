# Transpop — Changelog

> All notable changes to this project are documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
> See also: [[PROGRESS]] | [[ROADMAP]]

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
