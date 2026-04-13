from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ODMatrixComputeRequest(BaseModel):
    """Request to compute an OD matrix from active lignes."""

    beta: float = Field(default=0.08, gt=0, le=1.0, description="Distance decay parameter")
    k: float = Field(default=0.001, gt=0, description="Scaling constant")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ODMatrixEntry(BaseModel):
    """A single OD pair in the matrix."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    ligne_id: uuid.UUID | None
    origin_zone: str
    destination_zone: str
    flow_estimate: float
    distance_km: float
    gravity_score: float
    beta_used: float
    computed_at: datetime
    created_at: datetime
    updated_at: datetime


class ODMatrixListResponse(BaseModel):
    """List of OD matrix entries."""

    data: list[ODMatrixEntry]
    total: int
    beta_used: float


class ODMatrixComputeResponse(BaseModel):
    """Response after computing a new OD matrix."""

    entries_computed: int
    beta_used: float
    k_used: float
    entries: list[ODMatrixEntry]


# ---------------------------------------------------------------------------
# ZFE response schemas
# ---------------------------------------------------------------------------


class ZFEEndpointResult(BaseModel):
    """ZFE check result for a single coordinate."""

    lat: float
    lng: float
    is_in_zfe: bool
    zone_name: str | None = None
    restriction_level: str | None = None
    allowed_crit_air: list[int] | None = None


class ZFELigneResult(BaseModel):
    """ZFE compliance result for a single ligne."""

    ligne_id: str
    ligne_code: str
    ligne_name: str
    origin: ZFEEndpointResult
    dest: ZFEEndpointResult
    any_endpoint_in_zfe: bool
    checked_at: str


class ZFEComplianceResponse(BaseModel):
    """ZFE compliance check response for all lignes."""

    total_lignes: int
    lignes_in_zfe: int
    results: list[ZFELigneResult]


class ZFEPointCheckRequest(BaseModel):
    """Request to check a single point for ZFE compliance."""

    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class ZFEPointCheckResponse(BaseModel):
    """Response for a single ZFE point check."""

    is_in_zfe: bool
    zone_name: str | None = None
    restriction_level: str | None = None
    allowed_crit_air: list[int] | None = None
    checked_at: str


# ---------------------------------------------------------------------------
# Geocoding enrichment schemas
# ---------------------------------------------------------------------------


class GeocodingEnrichRequest(BaseModel):
    """Request to enrich a ligne with geocoded coordinates."""

    origin_address: str | None = None
    dest_address: str | None = None


class GeocodingEnrichResponse(BaseModel):
    """Response after geocoding enrichment."""

    ligne_id: str
    origin_geocoded: bool
    dest_geocoded: bool
    origin_lat: float | None = None
    origin_lng: float | None = None
    dest_lat: float | None = None
    dest_lng: float | None = None
