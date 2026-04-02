from __future__ import annotations

import io
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.services.export_engine import ExportEngine, load_optimization_context

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
