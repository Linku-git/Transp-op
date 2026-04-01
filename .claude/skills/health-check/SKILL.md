---
name: health-check
description: Verify all development services are running and healthy. Use to diagnose environment issues or after deploying locally.
---

# Health Check

Check all services and report status:

## 1. Docker Services
```bash
docker compose ps
```
Verify these are running and healthy:
- `db` (PostgreSQL 15 + PostGIS) — port 5432
- `redis` (Redis 7) — port 6379
- `backend` (FastAPI) — port 8000
- `frontend` (React/Vite dev server) — port 5173
- `osrm` (OSRM routing) — port 5000

Future services (not yet in docker-compose.yml):
- `celery` (Celery worker)
- `celery-beat` (Celery scheduler)

## 2. Database
```bash
docker compose exec db pg_isready -U postgres
docker compose exec db psql -U postgres -c "SELECT PostGIS_Version();"
```

## 3. Redis
```bash
docker compose exec redis redis-cli ping
```

## 4. Backend API
```bash
curl -s http://localhost:8000/health | python -m json.tool
curl -s http://localhost:8000/docs -o /dev/null -w "%{http_code}"
```

## 5. Frontend
```bash
docker compose ps frontend
curl -s http://localhost:5173 -o /dev/null -w "%{http_code}"
```
Check Docker container status first. If the container is not running, report it. If running but curl fails, check logs:
```bash
docker compose logs frontend --tail=10
```

## 6. OSRM
```bash
curl -s http://localhost:5000/health -o /dev/null -w "%{http_code}"
```

## 7. Alembic Migrations
```bash
cd backend && alembic current
cd backend && alembic check
```

## Report
Print a status dashboard:
```
Service          Status    Port    Details
─────────────────────────────────────────
PostgreSQL       ✓/✗       5432    PostGIS version
Redis            ✓/✗       6379    PONG
Backend API      ✓/✗       8000    /health response
Frontend         ✓/✗       5173    HTTP status
OSRM             ✓/✗       5000    HTTP status
Celery Worker    ✓/✗       -       Process status
Celery Beat      ✓/✗       -       Process status
Alembic          ✓/✗       -       Migration status
```
