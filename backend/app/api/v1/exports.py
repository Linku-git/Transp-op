from __future__ import annotations

import io
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.generated_report import GeneratedReport
from app.services.export_engine import ExportEngine, load_optimization_context
from app.services.report_engine import (
    generate_fleet_utilization_report,
    generate_hr_mobility_report,
    generate_modal_analysis_report,
    generate_volunteer_driver_report,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export")

ASYNC_THRESHOLD_ROUTES = 50


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def _get_engine(
    optimization_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> ExportEngine:
    """Load optimization context and build an ExportEngine."""
    context = await load_optimization_context(
        optimization_id=optimization_id,
        tenant_id=current_user.tenant_id,
        db=db,
    )
    return ExportEngine(context)


# ---------------------------------------------------------------------------
# GET /export/pdf
# ---------------------------------------------------------------------------


@router.get("/pdf")
async def export_pdf(
    optimization_id: uuid.UUID = Query(..., description="Optimization run UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate PDF driver sheets for an optimization run."""
    engine = await _get_engine(optimization_id, current_user, db)

    pdf_bytes = engine.generate_pdf()
    filename = f"routes_{str(optimization_id)[:8]}.pdf"

    return StreamingResponse(
        content=io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /export/excel
# ---------------------------------------------------------------------------


@router.get("/excel")
async def export_excel(
    optimization_id: uuid.UUID = Query(..., description="Optimization run UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate multi-sheet Excel workbook for an optimization run."""
    engine = await _get_engine(optimization_id, current_user, db)

    xlsx_bytes = engine.generate_excel()
    filename = f"optimization_{str(optimization_id)[:8]}.xlsx"

    return StreamingResponse(
        content=io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /export/csv/stops
# ---------------------------------------------------------------------------


@router.get("/csv/stops")
async def export_csv_stops(
    optimization_id: uuid.UUID = Query(..., description="Optimization run UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate CSV of ordered stops for an optimization run."""
    engine = await _get_engine(optimization_id, current_user, db)

    csv_text = engine.generate_csv_stops()
    filename = f"stops_{str(optimization_id)[:8]}.csv"

    return StreamingResponse(
        content=io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /export/csv/employees
# ---------------------------------------------------------------------------


@router.get("/csv/employees")
async def export_csv_employees(
    optimization_id: uuid.UUID = Query(..., description="Optimization run UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate CSV of employee assignments for an optimization run."""
    engine = await _get_engine(optimization_id, current_user, db)

    csv_text = engine.generate_csv_employees()
    filename = f"employees_{str(optimization_id)[:8]}.csv"

    return StreamingResponse(
        content=io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /export/geojson
# ---------------------------------------------------------------------------


@router.get("/geojson")
async def export_geojson(
    optimization_id: uuid.UUID = Query(..., description="Optimization run UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Generate GeoJSON FeatureCollection for an optimization run."""
    engine = await _get_engine(optimization_id, current_user, db)

    geojson = engine.generate_geojson()

    return JSONResponse(
        content=geojson,
        media_type="application/geo+json",
    )


# ---------------------------------------------------------------------------
# GET /export/history — list generated reports
# ---------------------------------------------------------------------------


@router.get("/history", response_model=dict)
async def list_generated_reports(
    report_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List generated report history for the current tenant."""
    from sqlalchemy import select, func
    conditions = [GeneratedReport.tenant_id == current_user.tenant_id]
    if report_type:
        conditions.append(GeneratedReport.report_type == report_type)

    count_stmt = select(func.count()).select_from(GeneratedReport).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    data_stmt = (
        select(GeneratedReport)
        .where(*conditions)
        .order_by(GeneratedReport.generated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(data_stmt)).scalars().all()

    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "data": [
            {
                "id": str(r.id),
                "report_type": r.report_type,
                "format": r.format,
                "params": r.params,
                "file_url": r.file_url,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                "generated_by": str(r.generated_by) if r.generated_by else None,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# Helper: persist GeneratedReport record
# ---------------------------------------------------------------------------


async def _persist_report(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    report_type: str,
    report_format: str,
) -> GeneratedReport:
    """Create and persist a GeneratedReport record."""
    report = GeneratedReport(
        tenant_id=tenant_id,
        report_type=report_type,
        format=report_format,
        generated_by=user_id,
        params={},
    )
    db.add(report)
    await db.flush()
    return report


# ---------------------------------------------------------------------------
# GET /export/modal-report
# ---------------------------------------------------------------------------


@router.get("/modal-report")
async def export_modal_report(
    report_format: str = Query(default="pdf", description="pdf or xlsx"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate modal analysis report (mode distribution and travel stats)."""
    report_bytes = await generate_modal_analysis_report(
        tenant_id=current_user.tenant_id,
        db=db,
        report_format=report_format,
    )

    await _persist_report(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        report_type="modal_analysis",
        report_format=report_format,
    )

    if report_format == "xlsx":
        return Response(
            content=report_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="modal_analysis.xlsx"'},
        )

    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="modal_analysis.pdf"'},
    )


# ---------------------------------------------------------------------------
# GET /export/fleet-report
# ---------------------------------------------------------------------------


@router.get("/fleet-report")
async def export_fleet_report(
    report_format: str = Query(default="pdf", description="pdf or xlsx"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate fleet utilization report."""
    report_bytes = await generate_fleet_utilization_report(
        tenant_id=current_user.tenant_id,
        db=db,
        report_format=report_format,
    )

    await _persist_report(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        report_type="fleet_utilization",
        report_format=report_format,
    )

    if report_format == "xlsx":
        return Response(
            content=report_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="fleet_utilization.xlsx"'},
        )

    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="fleet_utilization.pdf"'},
    )


# ---------------------------------------------------------------------------
# GET /export/volunteer-report
# ---------------------------------------------------------------------------


@router.get("/volunteer-report")
async def export_volunteer_report(
    report_format: str = Query(default="pdf", description="pdf or xlsx"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate volunteer driver report with driver details."""
    report_bytes = await generate_volunteer_driver_report(
        tenant_id=current_user.tenant_id,
        db=db,
        report_format=report_format,
    )

    await _persist_report(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        report_type="volunteer_driver",
        report_format=report_format,
    )

    if report_format == "xlsx":
        return Response(
            content=report_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="volunteer_drivers.xlsx"'},
        )

    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="volunteer_drivers.pdf"'},
    )


# ---------------------------------------------------------------------------
# GET /export/hr-mobility
# ---------------------------------------------------------------------------


@router.get("/hr-mobility")
async def export_hr_mobility(
    report_format: str = Query(default="pdf", description="pdf or xlsx"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate HR mobility report (coverage, shadow zones, etc.)."""
    report_bytes = await generate_hr_mobility_report(
        tenant_id=current_user.tenant_id,
        db=db,
        report_format=report_format,
    )

    await _persist_report(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        report_type="hr_mobility",
        report_format=report_format,
    )

    if report_format == "xlsx":
        return Response(
            content=report_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="hr_mobility.xlsx"'},
        )

    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="hr_mobility.pdf"'},
    )


# ---------------------------------------------------------------------------
# Sizing Plan Export (Session 82)
# ---------------------------------------------------------------------------

from app.middleware.auth import get_current_user
from app.schemas.sizing_plan_export import SizingPlanExportRequest, SizingPlanExportResponse
from app.services.export.sizing_plan_exporter import SizingPlanExporter


@router.post("/sizing-plan", response_model=SizingPlanExportResponse)
async def export_sizing_plan(
    body: SizingPlanExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SizingPlanExportResponse:
    """Generate a sizing plan export in JSON, XML, or PDF format."""
    exporter = SizingPlanExporter(db)
    export = await exporter.generate_export(
        tenant_id=current_user.tenant_id,
        optimization_id=body.optimization_id,
        operator_id=body.operator_id,
        export_format=body.format,
    )
    return SizingPlanExportResponse.model_validate(export)
