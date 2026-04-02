from __future__ import annotations

import asyncio
import json
import logging
import uuid

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis-based status tracking
# ---------------------------------------------------------------------------

_redis: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazily initialise and return a Redis client."""
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def set_export_status(
    optimization_id: uuid.UUID,
    export_format: str,
    status: str,
    progress: float = 0.0,
    error: str | None = None,
) -> None:
    """Store export progress in Redis (1 h TTL)."""
    r = _get_redis()
    key = f"export:{optimization_id}:{export_format}"
    data = {
        "status": status,
        "progress": progress,
        "format": export_format,
        "error": error or "",
    }
    r.set(key, json.dumps(data), ex=3600)


def get_export_status(
    optimization_id: uuid.UUID,
    export_format: str,
) -> dict | None:
    """Retrieve export progress from Redis."""
    r = _get_redis()
    key = f"export:{optimization_id}:{export_format}"
    raw = r.get(key)
    if raw is None:
        return None
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Celery setup (graceful degradation)
# ---------------------------------------------------------------------------

try:
    from celery import Celery

    celery_app = Celery(
        "transpop_exports",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.task_track_started = True
    celery_app.conf.task_time_limit = 120  # 2 min hard limit
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    celery_app = None
    logger.warning("Celery not available. Export tasks will run synchronously.")


# ---------------------------------------------------------------------------
# Main export task
# ---------------------------------------------------------------------------


async def run_export_task(
    optimization_id: str,
    tenant_id: str,
    export_format: str,
) -> dict:
    """Run an export generation task.

    Loads data from the database, generates the requested format,
    and stores the result bytes in Redis for retrieval.
    """
    from app.database import async_session_factory
    from app.services.export_engine import ExportEngine, load_optimization_context

    opt_id = uuid.UUID(optimization_id)
    t_id = uuid.UUID(tenant_id)

    set_export_status(opt_id, export_format, "running", 0.1)
    logger.info("Export %s/%s: starting", opt_id, export_format)

    try:
        async with async_session_factory() as session:
            context = await load_optimization_context(opt_id, t_id, session)

        set_export_status(opt_id, export_format, "running", 0.5)
        engine = ExportEngine(context)

        generators = {
            "pdf": engine.generate_pdf,
            "excel": engine.generate_excel,
            "csv_stops": engine.generate_csv_stops,
            "csv_employees": engine.generate_csv_employees,
            "geojson": engine.generate_geojson,
        }

        gen_func = generators.get(export_format)
        if gen_func is None:
            raise ValueError(f"Unknown export format: {export_format}")

        result = gen_func()

        # Store result in Redis for retrieval (10 min TTL)
        r = _get_redis()
        result_key = f"export_result:{opt_id}:{export_format}"
        if isinstance(result, bytes):
            r_raw = redis.from_url(settings.redis_url, decode_responses=False)
            r_raw.set(result_key, result, ex=600)
        elif isinstance(result, str):
            r.set(result_key, result, ex=600)
        elif isinstance(result, dict):
            r.set(result_key, json.dumps(result), ex=600)

        set_export_status(opt_id, export_format, "completed", 1.0)
        logger.info("Export %s/%s: completed", opt_id, export_format)

        return {
            "optimization_id": optimization_id,
            "format": export_format,
            "status": "completed",
        }

    except Exception as exc:
        logger.exception("Export %s/%s failed: %s", opt_id, export_format, exc)
        set_export_status(opt_id, export_format, "failed", 0.0, error=str(exc))
        return {
            "optimization_id": optimization_id,
            "format": export_format,
            "status": "failed",
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Synchronous wrapper for Celery
# ---------------------------------------------------------------------------


def run_export_sync(
    optimization_id: str,
    tenant_id: str,
    export_format: str,
) -> dict:
    """Synchronous wrapper for the async export task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            run_export_task(
                optimization_id=optimization_id,
                tenant_id=tenant_id,
                export_format=export_format,
            )
        )
    finally:
        loop.close()


# Register as a Celery task when the broker is available
if HAS_CELERY and celery_app is not None:
    export_pipeline_task = celery_app.task(
        name="transpop.export_pipeline",
        bind=False,
        queue="exports",
        max_retries=1,
    )(run_export_sync)
