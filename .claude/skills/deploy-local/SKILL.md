---
name: deploy-local
description: Start the local development environment. Starts Docker services, applies migrations, and prints access URLs.
---

# Deploy Local

1. Check Docker is running:
   ```bash
   docker info
   ```
2. Start services:
   ```bash
   docker compose up -d
   ```
3. Wait for health checks:
   ```bash
   docker compose exec db pg_isready
   docker compose exec redis redis-cli ping
   ```
4. Apply migrations:
   ```bash
   cd backend && alembic upgrade head
   ```
5. Verify services are healthy:
   ```bash
   docker compose ps
   ```
6. Print access URLs:
   - Backend API: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/docs
   - Frontend: http://localhost:5173
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379
   - OSRM: http://localhost:5000
