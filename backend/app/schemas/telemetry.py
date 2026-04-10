from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_SENSOR_TYPES = ["vibration", "temperature", "pressure", "can_bus", "battery_voltage", "engine_rpm", "speed"]


# ---------------------------------------------------------------------------
# Telemetry ingestion
# ---------------------------------------------------------------------------


class TelemetryReadingInput(BaseModel):
    """A single telemetry reading for batch ingestion."""

    vehicle_id: uuid.UUID
    timestamp: datetime
    sensor_type: str
    value: float
    unit: str | None = None
    metadata: dict | None = None

    @field_validator("sensor_type")
    @classmethod
    def validate_sensor_type(cls, v: str) -> str:
        if v not in VALID_SENSOR_TYPES:
            raise ValueError(f"sensor_type must be one of {VALID_SENSOR_TYPES}")
        return v


class TelemetryIngestRequest(BaseModel):
    """Batch telemetry ingestion request."""

    readings: list[TelemetryReadingInput] = Field(..., min_length=1)


class TelemetryIngestResponse(BaseModel):
    """Response from batch ingestion."""

    accepted: int
    rejected: int
    errors: list[dict]


# ---------------------------------------------------------------------------
# Predictive maintenance
# ---------------------------------------------------------------------------


class MaintenanceRunRequest(BaseModel):
    """Request to run predictive maintenance analysis."""

    vehicle_ids: list[uuid.UUID] | None = Field(default=None, description="Specific vehicles, or all if None")
    lookback_hours: int = Field(default=168, ge=1, description="Hours of telemetry to analyze (default 7d)")


class VehicleScore(BaseModel):
    """Anomaly score for a single vehicle."""

    vehicle_id: str
    anomaly_score: float
    severity: str
    is_anomalous: bool


class MaintenanceRunResponse(BaseModel):
    """Response from predictive maintenance run."""

    alerts_generated: int
    vehicles_scored: int
    scores: list[VehicleScore]
    model_info: dict


# ---------------------------------------------------------------------------
# Alert CRUD
# ---------------------------------------------------------------------------


class MaintenanceAlertResponse(BaseModel):
    """Maintenance alert record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vehicle_id: uuid.UUID
    alert_type: str
    severity: str
    anomaly_score: float
    features: dict | None
    acknowledged: bool
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert."""

    acknowledged: bool = True
