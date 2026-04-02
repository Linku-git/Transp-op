from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KmConsommationCreate(BaseModel):
    prestataire: str = Field(..., max_length=100)
    vehicle_type: str = Field(..., max_length=50)
    site_id: uuid.UUID | None = None
    vehicle_count_peak: int | None = Field(default=None, ge=0)
    km_avg: Decimal | None = None
    km_min: Decimal | None = None
    km_max: Decimal | None = None
    seat_count: int | None = Field(default=None, ge=0)
    fuel_consumption_l100km: Decimal | None = None
    monthly_cost_per_vehicle_mad: Decimal | None = None
    observations: str | None = None


class KmConsommationUpdate(BaseModel):
    prestataire: str | None = Field(default=None, max_length=100)
    vehicle_type: str | None = Field(default=None, max_length=50)
    site_id: uuid.UUID | None = None
    vehicle_count_peak: int | None = Field(default=None, ge=0)
    km_avg: Decimal | None = None
    km_min: Decimal | None = None
    km_max: Decimal | None = None
    seat_count: int | None = Field(default=None, ge=0)
    fuel_consumption_l100km: Decimal | None = None
    monthly_cost_per_vehicle_mad: Decimal | None = None
    observations: str | None = None


class KmConsommationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    prestataire: str
    vehicle_type: str
    vehicle_count_peak: int | None
    km_avg: Decimal | None
    km_min: Decimal | None
    km_max: Decimal | None
    seat_count: int | None
    fuel_consumption_l100km: Decimal | None
    monthly_cost_per_vehicle_mad: Decimal | None
    observations: str | None
    created_at: datetime
    updated_at: datetime

    site_name: str | None = None
