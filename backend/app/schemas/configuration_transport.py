from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConfigurationTransportCreate(BaseModel):
    ligne: str = Field(..., max_length=100)
    prestataire: str = Field(..., max_length=100)
    site_id: uuid.UUID | None = None
    vehicle_type: str | None = Field(default=None, max_length=50)
    vehicle_count: int | None = Field(default=None, ge=0)
    shift: str | None = Field(default=None, max_length=20)
    point_depart_id: uuid.UUID | None = None
    point_arrivee_id: uuid.UUID | None = None
    circuit: str | None = Field(default=None, max_length=200)
    is_active: bool = True
    observations: str | None = None


class ConfigurationTransportUpdate(BaseModel):
    ligne: str | None = Field(default=None, max_length=100)
    prestataire: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None
    vehicle_type: str | None = Field(default=None, max_length=50)
    vehicle_count: int | None = Field(default=None, ge=0)
    shift: str | None = Field(default=None, max_length=20)
    point_depart_id: uuid.UUID | None = None
    point_arrivee_id: uuid.UUID | None = None
    circuit: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None
    observations: str | None = None


class ConfigurationTransportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    ligne: str
    prestataire: str
    vehicle_type: str | None
    vehicle_count: int | None
    shift: str | None
    point_depart_id: uuid.UUID | None
    point_arrivee_id: uuid.UUID | None
    circuit: str | None
    is_active: bool
    observations: str | None
    created_at: datetime
    updated_at: datetime

    site_name: str | None = None
    point_depart_nom: str | None = None
    point_arrivee_nom: str | None = None
