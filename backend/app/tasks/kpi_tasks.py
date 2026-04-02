from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


async def _run_daily_snapshot() -> int:
    """Async implementation of the daily KPI snapshot capture."""
    from sqlalchemy import select

    from app.database import async_session_factory
    from app.models.auth import Tenant
    from app.services.kpi_service import capture_all_sites_snapshots

    total = 0
    async with async_session_factory() as session:
        async with session.begin():
            stmt = select(Tenant).where(Tenant.is_active.is_(True))
            result = await session.execute(stmt)
            tenants = result.scalars().all()

            for tenant in tenants:
                count = await capture_all_sites_snapshots(tenant.id, session)
                total += count

    logger.info(
        "Daily KPI snapshot: %d snapshots created for %d tenants",
        total,
        len(tenants),
    )
    return total


def daily_kpi_snapshot() -> int:
    """Celery task: capture KPI snapshots for all tenants and sites.

    This synchronous wrapper creates a new event loop to run the async
    implementation, following the same pattern as optimization_tasks.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_run_daily_snapshot())
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Register as Celery task when broker is available
# ---------------------------------------------------------------------------

try:
    from app.tasks.optimization_tasks import celery_app, HAS_CELERY

    if HAS_CELERY and celery_app is not None:
        daily_kpi_snapshot_task = celery_app.task(
            name="transpop.daily_kpi_snapshot",
            bind=False,
            queue="reports",
            max_retries=1,
        )(daily_kpi_snapshot)
except ImportError:
    logger.warning("Celery not available for KPI snapshot tasks.")
