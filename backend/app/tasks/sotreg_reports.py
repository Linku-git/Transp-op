"""Celery tasks for SOTREG MCDA report generation.

Session 113 — async PDF/Excel generation via Celery workers with
Redis-based status tracking and graceful fallback.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis status tracking
# ---------------------------------------------------------------------------

_redis: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazily initialise and return a Redis client."""
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def set_report_status(
    scenario_id: uuid.UUID,
    report_format: str,
    status: str,
    progress: float = 0.0,
    error: str | None = None,
) -> None:
    """Store report generation progress in Redis (1 h TTL)."""
    r = _get_redis()
    key = f"mcda_report:{scenario_id}:{report_format}"
    data = {
        "status": status,
        "progress": progress,
        "format": report_format,
        "error": error or "",
    }
    r.set(key, json.dumps(data), ex=3600)


def get_report_status(
    scenario_id: uuid.UUID,
    report_format: str,
) -> dict | None:
    """Retrieve report generation progress from Redis."""
    r = _get_redis()
    key = f"mcda_report:{scenario_id}:{report_format}"
    raw = r.get(key)
    if raw is None:
        return None
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Async report generation
# ---------------------------------------------------------------------------


async def run_mcda_report_task(
    scenario_id: str,
    tenant_id: str,
    report_format: str,
) -> dict:
    """Generate an MCDA report asynchronously.

    Loads the scenario from DB, generates the requested format,
    and stores the result bytes in Redis for retrieval.

    Args:
        scenario_id: UUID string of the MCDAScenario.
        tenant_id: UUID string of the tenant.
        report_format: ``"pdf"`` or ``"xlsx"``.

    Returns:
        Dict with status and metadata.
    """
    from app.database import async_session_factory
    from app.services.sotreg.mcda_report import generate_mcda_report

    s_id = uuid.UUID(scenario_id)
    set_report_status(s_id, report_format, "running", 0.1)
    logger.info("MCDA report %s/%s: starting", s_id, report_format)

    try:
        async with async_session_factory() as session:
            report_bytes = await generate_mcda_report(s_id, session, report_format)

        if report_bytes is None:
            set_report_status(s_id, report_format, "failed", 0.0, error="Scenario not found")
            return {
                "scenario_id": scenario_id,
                "format": report_format,
                "status": "failed",
                "error": "Scenario not found",
            }

        set_report_status(s_id, report_format, "running", 0.8)

        # Store result bytes in Redis (10 min TTL)
        r_raw = redis.from_url(settings.redis_url, decode_responses=False)
        result_key = f"mcda_report_result:{s_id}:{report_format}"
        r_raw.set(result_key, report_bytes, ex=600)

        set_report_status(s_id, report_format, "completed", 1.0)
        logger.info(
            "MCDA report %s/%s: completed (%d bytes)",
            s_id, report_format, len(report_bytes),
        )

        return {
            "scenario_id": scenario_id,
            "format": report_format,
            "status": "completed",
            "size_bytes": len(report_bytes),
        }

    except Exception as exc:
        logger.exception("MCDA report %s/%s failed: %s", s_id, report_format, exc)
        set_report_status(s_id, report_format, "failed", 0.0, error=str(exc))
        return {
            "scenario_id": scenario_id,
            "format": report_format,
            "status": "failed",
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Synchronous wrapper for Celery
# ---------------------------------------------------------------------------


def run_mcda_report_sync(
    scenario_id: str,
    tenant_id: str,
    report_format: str,
) -> dict:
    """Synchronous wrapper that Celery can invoke."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            run_mcda_report_task(scenario_id, tenant_id, report_format)
        )
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Celery task registration (graceful degradation)
# ---------------------------------------------------------------------------

try:
    from celery import Celery

    celery_app = Celery(
        "transpop_mcda_reports",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.task_track_started = True
    celery_app.conf.task_time_limit = 300  # 5 min hard limit
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    celery_app = None
    logger.warning("Celery not available. MCDA report tasks will run synchronously.")

if HAS_CELERY and celery_app is not None:
    mcda_report_task = celery_app.task(
        name="transpop.mcda_report",
        bind=False,
        queue="sotreg",
        max_retries=1,
    )(run_mcda_report_sync)
