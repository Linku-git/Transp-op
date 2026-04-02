from __future__ import annotations

import logging
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.kpi_snapshot import KPISnapshot
from app.models.modal import EmployeeModal
from app.models.optimization import Optimization
from app.models.site import Site
from app.services.hr_analytics import compute_mobility_coverage
from app.services.rse_analytics import compute_co2_savings

logger = logging.getLogger(__name__)

KPI_TYPES: list[str] = [
    "mobility_coverage",
    "modal_distribution",
    "occupancy_rate",
    "co2_saved",
    "rti_compliance",
    "security_score",
]


# ---------------------------------------------------------------------------
# Individual KPI computations
# ---------------------------------------------------------------------------


async def _compute_mobility_coverage_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """Extract coverage percentage from hr_analytics."""
    result = await compute_mobility_coverage(tenant_id, db)
    # If site_id is given, try to find it in the by_site breakdown
    if site_id is not None:
        for site_data in result.get("by_site", []):
            # Match is tricky by name; use overall for now
            pass
    return {
        "coverage_pct": result.get("coverage_pct", 0),
        "total_employees": result.get("total_employees", 0),
        "covered_employees": result.get("covered_employees", 0),
    }


async def _compute_modal_distribution_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """Compute mode share percentages from EmployeeModal."""
    from sqlalchemy import func

    base_filters = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        base_filters.append(Employee.site_id == site_id)

    stmt = (
        select(
            EmployeeModal.primary_mode,
            func.count().label("count"),
        )
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*base_filters)
        .group_by(EmployeeModal.primary_mode)
        .order_by(func.count().desc())
    )
    rows = (await db.execute(stmt)).all()
    total = sum(r.count for r in rows)

    distribution: dict[str, float] = {}
    for r in rows:
        mode = r.primary_mode or "unknown"
        distribution[mode] = round(r.count / total * 100, 1) if total > 0 else 0

    return {"total_employees": total, "distribution": distribution}


async def _compute_occupancy_rate_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """Average vehicle occupancy from the latest completed optimizations."""
    from sqlalchemy import func

    filters = [
        Optimization.tenant_id == tenant_id,
        Optimization.status == "completed",
    ]
    if site_id is not None:
        filters.append(Optimization.site_id == site_id)

    stmt = (
        select(
            func.avg(
                Optimization.metrics["avg_occupancy_rate"].as_float()
            ).label("avg_occ"),
        )
        .where(*filters)
    )
    result = await db.execute(stmt)
    avg_occ = result.scalar_one_or_none()

    return {"occupancy_rate_pct": round(float(avg_occ), 1) if avg_occ else 0}


async def _compute_co2_saved_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """CO2 savings from rse_analytics."""
    result = await compute_co2_savings(tenant_id, db)
    return {
        "co2_saved_kg": result.get("co2_saved_kg", 0),
        "co2_saved_pct": result.get("co2_saved_pct", 0),
    }


async def _compute_rti_compliance_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """Placeholder until Session 58."""
    return {"compliance_pct": 0}


async def _compute_security_score_value(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """Placeholder until Session 62."""
    return {"score": 0}


_KPI_COMPUTERS: dict[str, Any] = {
    "mobility_coverage": _compute_mobility_coverage_value,
    "modal_distribution": _compute_modal_distribution_value,
    "occupancy_rate": _compute_occupancy_rate_value,
    "co2_saved": _compute_co2_saved_value,
    "rti_compliance": _compute_rti_compliance_value,
    "security_score": _compute_security_score_value,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def capture_kpi_snapshot(
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None,
    db: AsyncSession,
) -> list[KPISnapshot]:
    """Capture all KPI types for a given site on today's date.

    Returns the list of created KPISnapshot records.
    """
    today = date.today()
    snapshots: list[KPISnapshot] = []

    for kpi_type in KPI_TYPES:
        computer = _KPI_COMPUTERS[kpi_type]
        value = await computer(tenant_id, site_id, db)

        snapshot = KPISnapshot(
            tenant_id=tenant_id,
            site_id=site_id,
            snapshot_date=today,
            kpi_type=kpi_type,
            value=value,
        )
        db.add(snapshot)
        snapshots.append(snapshot)

    await db.flush()
    logger.info(
        "Captured %d KPI snapshots for tenant %s site %s on %s",
        len(snapshots),
        tenant_id,
        site_id,
        today,
    )
    return snapshots


async def capture_all_sites_snapshots(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> int:
    """Capture snapshots for all sites in a tenant.

    Returns total count of snapshots created.
    """
    stmt = select(Site).where(Site.tenant_id == tenant_id)
    result = await db.execute(stmt)
    sites = result.scalars().all()

    total = 0
    for site in sites:
        snaps = await capture_kpi_snapshot(tenant_id, site.id, db)
        total += len(snaps)

    # Also capture tenant-wide (site_id=None)
    snaps = await capture_kpi_snapshot(tenant_id, None, db)
    total += len(snaps)

    logger.info(
        "Captured %d total snapshots for tenant %s across %d sites",
        total,
        tenant_id,
        len(sites),
    )
    return total


async def get_kpi_trend(
    tenant_id: uuid.UUID,
    db: AsyncSession,
    kpi_type: str,
    site_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """Query historical KPI snapshots for trend charts.

    Returns a list of ``{snapshot_date, value, site_id}`` ordered by date ascending.
    """
    filters = [
        KPISnapshot.tenant_id == tenant_id,
        KPISnapshot.kpi_type == kpi_type,
    ]
    if site_id is not None:
        filters.append(KPISnapshot.site_id == site_id)
    if start_date is not None:
        filters.append(KPISnapshot.snapshot_date >= start_date)
    if end_date is not None:
        filters.append(KPISnapshot.snapshot_date <= end_date)

    stmt = (
        select(KPISnapshot)
        .where(*filters)
        .order_by(KPISnapshot.snapshot_date.asc())
        .limit(365)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [
        {
            "snapshot_date": str(row.snapshot_date),
            "value": row.value,
            "site_id": str(row.site_id) if row.site_id else None,
        }
        for row in rows
    ]
