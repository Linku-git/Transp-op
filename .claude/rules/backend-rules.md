# Backend Rules (Python/FastAPI)

## File Structure
- Models: `backend/app/models/<module>.py` — one file per domain module
- Schemas: `backend/app/schemas/<module>.py` — Pydantic v2 request/response models
- Routes: `backend/app/api/v1/<module>.py` — route handlers
- Services: `backend/app/services/<name>.py` — business logic (no route imports)
- Tasks: `backend/app/tasks/<name>.py` — Celery async tasks
- Config: `backend/app/config.py` — Pydantic Settings (env vars)

## Conventions
- All functions must have type annotations (params + return)
- Use `async def` for all route handlers and I/O-bound functions
- Use Pydantic v2 models for ALL request/response validation
- Use SQLAlchemy ORM exclusively, no raw SQL unless documented with justification
- Use `from __future__ import annotations` in all files
- Pagination: default page_size=20, max=100, format: `{data, total, page, pages}`
- Error format: `{"detail": "message", "code": "ERROR_CODE"}`
- Logging via `logging` module, never `print()`
- All endpoints behind auth middleware (except `/health` and `/`)
- PostGIS for all geospatial operations (ST_Distance, ST_DWithin, ST_MakePoint)

## Dependencies
- FastAPI, SQLAlchemy 2.0, GeoAlchemy2, Pydantic v2, Alembic
- Celery + Redis for async tasks >5 seconds
- OR-Tools for vehicle routing (CVRP)
- scikit-learn for clustering (DBSCAN, KMeans)

## Import Order
1. Standard library
2. Third-party packages
3. Local application imports (absolute: `from app.models.site import Site`)
