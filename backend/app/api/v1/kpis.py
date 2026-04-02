from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.services.hr_analytics import compute_hr_kpis
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
