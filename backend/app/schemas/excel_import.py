from __future__ import annotations

from pydantic import BaseModel


class ImportErrorResponse(BaseModel):
    """A single validation or import error tied to a specific cell."""

    sheet: str
    row: int
    column: str
    message: str


class SheetResultResponse(BaseModel):
    """Import outcome for one sheet."""

    sheet: str
    rows_parsed: int
    rows_imported: int
    rows_skipped: int
    errors: list[ImportErrorResponse]


class ImportResultResponse(BaseModel):
    """Aggregate import outcome across all processed sheets."""

    sheets: list[SheetResultResponse]
    total_errors: int
    is_preview: bool
