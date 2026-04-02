from __future__ import annotations

import logging
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.services.hr_analytics import compute_hr_kpis
from app.services.kpi_service import (
    KPI_TYPES,
    capture_all_sites_snapshots,
    capture_kpi_snapshot,
    get_kpi_trend,
)
from app.services.rse_analytics import compute_rse_kpis, generate_dpef_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis")


@router.get("/hr", response_model=dict)
async def get_hr_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all HR dashboard KPIs: mobility coverage, absenteeism, retention, shadow zones."""
    result = await compute_hr_kpis(current_user.tenant_id, db)
    logger.info("HR KPIs computed for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return result


@router.get("/rse", response_model=dict)
async def get_rse_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all RSE (Corporate Social Responsibility) KPIs: CO2 savings, modal distribution, ZFE compliance."""
    result = await compute_rse_kpis(current_user.tenant_id, db)
    logger.info("RSE KPIs computed for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return result


@router.post("/rse/dpef")
async def export_dpef_report(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate and download a DPEF (Declaration de Performance Extra-Financiere) PDF report."""
    rse_data = await compute_rse_kpis(current_user.tenant_id, db)
    pdf_bytes = generate_dpef_pdf(rse_data)
    logger.info("DPEF report generated for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=rapport_dpef.pdf",
        },
    )


@router.post("/snapshot", response_model=dict)
async def create_kpi_snapshot(
    site_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Capture KPI snapshot for a site (or all sites if site_id is None)."""
    if site_id is not None:
        snapshots = await capture_kpi_snapshot(current_user.tenant_id, site_id, db)
        logger.info(
            "KPI snapshot captured for site %s by user %s",
            site_id,
            current_user.id,
        )
        return {
            "data": {
                "count": len(snapshots),
                "site_id": str(site_id),
                "kpi_types": [s.kpi_type for s in snapshots],
            }
        }
    else:
        count = await capture_all_sites_snapshots(current_user.tenant_id, db)
        logger.info(
            "KPI snapshots captured for all sites by user %s (%d total)",
            current_user.id,
            count,
        )
        return {
            "data": {
                "count": count,
                "site_id": None,
                "kpi_types": KPI_TYPES,
            }
        }


@router.get("/trend", response_model=dict)
async def get_kpi_trend_data(
    kpi_type: str = Query(...),
    site_id: uuid.UUID | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get historical KPI trend data for dashboard charts."""
    if kpi_type not in KPI_TYPES:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail=f"Invalid kpi_type '{kpi_type}'. Must be one of: {KPI_TYPES}",
        )

    parsed_start = date.fromisoformat(start_date) if start_date else None
    parsed_end = date.fromisoformat(end_date) if end_date else None

    trend = await get_kpi_trend(
        tenant_id=current_user.tenant_id,
        db=db,
        kpi_type=kpi_type,
        site_id=site_id,
        start_date=parsed_start,
        end_date=parsed_end,
    )
    logger.info(
        "KPI trend queried: type=%s site=%s range=%s..%s (%d points)",
        kpi_type,
        site_id,
        start_date,
        end_date,
        len(trend),
    )
    return {"data": trend}
