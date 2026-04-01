from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.schemas.excel_import import (
    ImportErrorResponse,
    ImportResultResponse,
    SheetResultResponse,
)
from app.services.excel_parser import (
    ALL_SHEETS,
    ExcelImportService,
    ImportResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import")

# Accepted MIME types for .xlsx files
_XLSX_MIME_TYPES = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _result_to_response(result: ImportResult) -> ImportResultResponse:
    """Convert the internal ImportResult dataclass to the Pydantic response model."""
    return ImportResultResponse(
        sheets=[
            SheetResultResponse(
                sheet=sr.sheet,
                rows_parsed=sr.rows_parsed,
                rows_imported=sr.rows_imported,
                rows_skipped=sr.rows_skipped,
                errors=[
                    ImportErrorResponse(
                        sheet=e.sheet,
                        row=e.row,
                        column=e.column,
                        message=e.message,
                    )
                    for e in sr.errors
                ],
            )
            for sr in result.sheets
        ],
        total_errors=result.total_errors,
        is_preview=result.is_preview,
    )


def _validate_file(file: UploadFile) -> None:
    """Raise 422 if the uploaded file is not an xlsx."""
    if file.content_type not in _XLSX_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be an Excel (.xlsx) spreadsheet",
        )


# ---------------------------------------------------------------------------
# POST /import/excel — full import
# ---------------------------------------------------------------------------


@router.post("/excel", response_model=ImportResultResponse)
async def import_excel(
    file: UploadFile,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ImportResultResponse:
    """Upload and import a full multi-sheet Excel template.

    Processes all recognised sheets (SITES, EFFECTIF, USAGES & MODES,
    CONTRAINTES, PARC EXISTANT, ABSENCES) and performs upserts where
    applicable.
    """
    _validate_file(file)
    file_bytes = await file.read()

    service = ExcelImportService(db=db, tenant_id=current_user.tenant_id)
    result = await service.parse_and_import(file_bytes, preview=False)

    logger.info(
        "Excel full import by user %s: %d total errors across %d sheets",
        current_user.id,
        result.total_errors,
        len(result.sheets),
    )
    return _result_to_response(result)


# ---------------------------------------------------------------------------
# POST /import/excel/preview — validation only (no DB writes)
# ---------------------------------------------------------------------------


@router.post("/excel/preview", response_model=ImportResultResponse)
async def preview_excel(
    file: UploadFile,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ImportResultResponse:
    """Parse and validate an Excel template without writing to the database.

    Useful for showing the user what *would* happen before committing.
    """
    _validate_file(file)
    file_bytes = await file.read()

    service = ExcelImportService(db=db, tenant_id=current_user.tenant_id)
    result = await service.parse_and_import(file_bytes, preview=True)

    logger.info(
        "Excel preview by user %s: %d total errors across %d sheets",
        current_user.id,
        result.total_errors,
        len(result.sheets),
    )
    return _result_to_response(result)


# ---------------------------------------------------------------------------
# POST /import/excel/sheet — single sheet import
# ---------------------------------------------------------------------------


@router.post("/excel/sheet", response_model=ImportResultResponse)
async def import_excel_sheet(
    file: UploadFile,
    sheet_name: str = Query(
        ...,
        description="Name of the sheet to import",
    ),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ImportResultResponse:
    """Import a single sheet from the Excel template.

    The *sheet_name* query parameter must match one of the recognised sheet
    names exactly.
    """
    _validate_file(file)

    if sheet_name not in ALL_SHEETS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown sheet name '{sheet_name}'. Must be one of: {', '.join(ALL_SHEETS)}",
        )

    file_bytes = await file.read()

    service = ExcelImportService(db=db, tenant_id=current_user.tenant_id)
    result = await service.parse_and_import(file_bytes, preview=False, sheet_name=sheet_name)

    logger.info(
        "Excel single-sheet import (%s) by user %s: %d errors",
        sheet_name,
        current_user.id,
        result.total_errors,
    )
    return _result_to_response(result)
