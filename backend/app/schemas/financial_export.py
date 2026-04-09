from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FinancialExportRequest(BaseModel):
    target_system: str = Field(..., pattern=r"^(sap_fi|sage|cegid)$")
    company_code: str = "1000"
    currency: str = "MAD"


class FinancialExportResponse(BaseModel):
    target_system: str
    file_name: str
    content_type: str
    generated_at: datetime
    entries_count: int
