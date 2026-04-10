from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.maintenance_alert import MaintenanceAlert
from app.models.telemetry_reading import TelemetryReading
from app.schemas.telemetry import (
    AlertAcknowledgeRequest,
    MaintenanceAlertResponse,
    MaintenanceRunRequest,
    MaintenanceRunResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    VehicleScore,
)
from app.services.sotreg.telemetry_ingestion import process_telemetry_batch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/telemetry")


# ---------------------------------------------------------------------------
# POST /sotreg/telemetry/ingest — batch ingestion
# ---------------------------------------------------------------------------


@router.post("/ingest", response_model=TelemetryIngestResponse)
async def ingest_telemetry(
    body: TelemetryIngestRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> TelemetryIngestResponse:
    """Ingest a batch of telemetry readings from vehicle sensors."""
    readings_data = [
        {
            "vehicle_id": str(r.vehicle_id),
            "timestamp": r.timestamp,
            "sensor_type": r.sensor_type,
            "value": r.value,
            "unit": r.unit,
            "metadata": r.metadata,
        }
        for r in body.readings
    ]

    result = process_telemetry_batch(readings_data)

    # Persist accepted readings
    for r in body.readings:
        reading = TelemetryReading(
            tenant_id=current_user.tenant_id,
            vehicle_id=r.vehicle_id,
            reading_timestamp=r.timestamp,
            sensor_type=r.sensor_type,
            value=r.value,
            unit=r.unit,
            reading_metadata=r.metadata,
        )
        db.add(reading)

    await db.flush()

    logger.info(
        "Telemetry ingested: %d accepted, %d rejected by user %s",
        result["accepted"],
        result["rejected"],
        current_user.id,
    )

    return TelemetryIngestResponse(
        accepted=result["accepted"],
        rejected=result["rejected"],
        errors=result["errors"],
    )


# ---------------------------------------------------------------------------
# GET /sotreg/telemetry/alerts — list maintenance alerts
# ---------------------------------------------------------------------------


@router.get("/alerts", response_model=list[MaintenanceAlertResponse])
async def list_alerts(
    vehicle_id: uuid.UUID | None = Query(default=None),
    severity: str | None = Query(default=None),
    acknowledged: bool | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[MaintenanceAlert]:
    """List maintenance alerts with optional filters."""
    conditions = [MaintenanceAlert.tenant_id == current_user.tenant_id]
    if vehicle_id is not None:
        conditions.append(MaintenanceAlert.vehicle_id == vehicle_id)
    if severity is not None:
        conditions.append(MaintenanceAlert.severity == severity)
    if acknowledged is not None:
        conditions.append(MaintenanceAlert.acknowledged == acknowledged)

    stmt = (
        select(MaintenanceAlert)
        .where(*conditions)
        .order_by(MaintenanceAlert.created_at.desc())
        .limit(100)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# GET /sotreg/telemetry/alerts/{vehicle_id} — vehicle-specific alerts
# ---------------------------------------------------------------------------


@router.get("/alerts/{vehicle_id}", response_model=list[MaintenanceAlertResponse])
async def get_vehicle_alerts(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[MaintenanceAlert]:
    """Get maintenance alerts for a specific vehicle."""
    stmt = (
        select(MaintenanceAlert)
        .where(
            MaintenanceAlert.tenant_id == current_user.tenant_id,
            MaintenanceAlert.vehicle_id == vehicle_id,
        )
        .order_by(MaintenanceAlert.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# PUT /sotreg/telemetry/alerts/{alert_id}/acknowledge
# ---------------------------------------------------------------------------


@router.put("/alerts/{alert_id}/acknowledge", response_model=MaintenanceAlertResponse)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    body: AlertAcknowledgeRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceAlert:
    """Acknowledge a maintenance alert."""
    stmt = select(MaintenanceAlert).where(
        MaintenanceAlert.id == alert_id,
        MaintenanceAlert.tenant_id == current_user.tenant_id,
    )
    alert = (await db.execute(stmt)).scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.acknowledged = body.acknowledged
    await db.flush()
    await db.refresh(alert)

    logger.info("Alert %s acknowledged=%s by user %s", alert_id, body.acknowledged, current_user.id)
    return alert
