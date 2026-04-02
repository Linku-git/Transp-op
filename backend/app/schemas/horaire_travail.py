from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HoraireTravailCreate(BaseModel):
    type_horaire: str = Field(..., max_length=100)
    site_id: uuid.UUID | None = None
    depart_h1: str | None = Field(default=None, max_length=10, description="HH:MM")
    retour_h1: str | None = Field(default=None, max_length=10, description="HH:MM")
    depart_h2: str | None = Field(default=None, max_length=10, description="HH:MM")
    retour_h2: str | None = Field(default=None, max_length=10, description="HH:MM")
    observations: str | None = None


class HoraireTravailUpdate(BaseModel):
    type_horaire: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None
    depart_h1: str | None = Field(default=None, max_length=10)
    retour_h1: str | None = Field(default=None, max_length=10)
    depart_h2: str | None = Field(default=None, max_length=10)
    retour_h2: str | None = Field(default=None, max_length=10)
    observations: str | None = None


class HoraireTravailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    type_horaire: str
    depart_h1: str | None
    retour_h1: str | None
    depart_h2: str | None
    retour_h2: str | None
    observations: str | None
    created_at: datetime
    updated_at: datetime

    site_name: str | None = None
