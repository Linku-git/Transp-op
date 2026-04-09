from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.financial_export import FinancialExportRequest, FinancialExportResponse
from app.services.erp_export import ERPExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial")


@router.post("/export/daf")
async def export_daf(
    body: FinancialExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate financial export for DAF team in ERP-compatible format."""
    service = ERPExportService()

    # Build sample financial data (in production, query from DB)
    financial_data = service.build_financial_data(
        tco_entries=[
            {"account": "6200000", "amount": 150000, "description": "TCO Flotte transport", "cost_center": "CC100"},
            {"account": "6200100", "amount": 25000, "description": "Maintenance véhicules", "cost_center": "CC100"},
            {"account": "6200200", "amount": 18000, "description": "Carburant", "cost_center": "CC100"},
        ],
        roi_entries=[
            {"account": "6300000", "amount": -45000, "description": "Économies absentéisme", "cost_center": "CC100"},
            {"account": "6300100", "amount": -30000, "description": "Économies turnover", "cost_center": "CC100"},
        ],
        cost_per_trip={"cost_per_trip": 12.50, "total_cost": 375000, "total_trips": 30000},
        investment_comparator={"recommended_model": "OPEX", "annual_cost": 180000},
        company_code=body.company_code,
        currency=body.currency,
    )

    content, content_type, extension = service.generate_export(
        body.target_system, financial_data
    )

    filename = f"transpop_daf_{body.target_system}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.{extension}"

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
