from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PointArretCreate(BaseModel):
    code: str = Field(..., max_length=30)
    nom: str = Field(..., max_length=200)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    adresse: str | None = None
    ville: str | None = Field(default=None, max_length=100)
    prestataire: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None
    is_active: bool = True
    correspondance_tb: str | None = None
    observations: str | None = None


class PointArretUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=30)
    nom: str | None = Field(default=None, max_length=200)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    adresse: str | None = None
    ville: str | None = Field(default=None, max_length=100)
    prestataire: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None
    is_active: bool | None = None
    correspondance_tb: str | None = None
    observations: str | None = None


class PointArretResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    code: str
    nom: str
    adresse: str | None
    ville: str | None
    lat: float
    lng: float
    prestataire: str | None
    is_active: bool
    correspondance_tb: str | None
    observations: str | None
    created_at: datetime
    updated_at: datetime

    site_name: str | None = None
