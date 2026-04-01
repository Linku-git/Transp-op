# Transpop — HR Mobility Orchestration Platform

Enterprise SaaS platform for optimizing employee transport: clustering, route optimization, financial engineering, real-time tracking, and journey valorization.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, GeoAlchemy2, Celery |
| Database | PostgreSQL 15 + PostGIS, Redis 7 |
| Frontend | React 18, TypeScript, Vite, TailwindCSS, Leaflet, Recharts |
| Mobile | Flutter (Dart), Riverpod, Google Maps, Firebase FCM |
| Infra | Docker Compose (dev), Kubernetes (prod), GitHub Actions |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Run

```bash
# Clone the repository
git clone <repo-url> && cd transpop

# Start all services
docker compose up -d

# Verify services are running
docker compose ps
```

### Access Points

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| OSRM | http://localhost:5000 |

### Verify Setup

```bash
# Check PostgreSQL + PostGIS
docker compose exec db psql -U transpop -c "SELECT PostGIS_Version();"

# Check Redis
docker compose exec redis redis-cli ping

# Check Backend API
curl http://localhost:8000/health
```

## Project Structure

```
backend/    — FastAPI application (Python)
frontend/   — React web dashboard (TypeScript)
mobile/     — Flutter mobile app (Dart)
Docs/       — Project documentation (Obsidian vault)
```

## Development

This project follows a 92-session development roadmap. See `Docs/ROADMAP.md` for details.

Each session uses the workflow:
1. `/session-start <number>` — load context, create branch
2. Implement tasks from `Docs/sessions/session-XX.md`
3. `/session-end <number> <status>` — test, update docs, commit
