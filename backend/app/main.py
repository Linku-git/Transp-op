from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.config import settings
from app.database import async_session_factory, engine
from app.db.seed_vehicles import seed_vehicle_references

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Resolve the path to the built frontend assets (relative to this file)
_FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Transpop API (%s)", settings.environment)
    # Seed vehicle reference catalog
    async with async_session_factory() as session:
        async with session.begin():
            await seed_vehicle_references(session)
    yield
    logger.info("Shutting down Transpop API")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="HR Mobility Orchestration Platform",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability
from app.middleware.metrics import setup_metrics
from app.middleware.tracing import setup_tracing

setup_metrics(app)
setup_tracing()

app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Serve the React SPA in production (when dist/ exists)
# ---------------------------------------------------------------------------

if _FRONTEND_DIST.is_dir():
    # Serve Vite's static assets folder (JS, CSS, images)
    _assets_dir = _FRONTEND_DIST / "assets"
    if _assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    # Serve any other static file from the dist root
    app.mount(
        "/static",
        StaticFiles(directory=str(_FRONTEND_DIST)),
        name="static-root",
    )

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = "") -> FileResponse:
        """Catch-all: return index.html for all non-API routes (SPA routing)."""
        # Never intercept API or docs routes
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "health")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        candidate = _FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))

else:
    @app.get("/")
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
        }
