from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class FleetContextResponse(BaseModel):
    """Fleet diagnostics snapshot returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    total_vehicles: int
    total_km_annual: float
    total_tco2_annual: float
    average_age_years: float | None
    pct_diesel: float
    pct_electric: float
    pct_hybrid: float
    currency: str
    snapshot_date: date
    created_at: datetime
    updated_at: datetime
