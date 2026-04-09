"""RGPD compliance API endpoints."""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.services.gdpr import (
    export_employee_data,
    gdpr_delete_employee,
    record_consent,
    withdraw_consent,
    get_retention_policy,
    RGPD_CHECKLIST,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/employees/{employee_id}/export-data")
async def export_data(
    employee_id: uuid.UUID,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Right of access — export all personal data for an employee."""
    try:
        data = await export_employee_data(
            db, employee_id, current_user.tenant_id, format
        )
        return {"format": format, "data": data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/employees/{employee_id}/gdpr-delete")
async def gdpr_delete(
    employee_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Right to erasure — delete all personal data."""
    try:
        return await gdpr_delete_employee(
            db, employee_id, current_user.tenant_id,
            requested_by=str(current_user.id),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/consent")
async def grant_consent(
    employee_id: uuid.UUID,
    consent_type: str = "geolocation",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Record explicit consent."""
    return await record_consent(db, employee_id, consent_type, granted=True)


@router.delete("/consent")
async def revoke_consent(
    employee_id: uuid.UUID,
    consent_type: str = "geolocation",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Withdraw consent and stop data collection."""
    return await withdraw_consent(db, employee_id, consent_type)


@router.get("/rgpd/retention-policy")
async def retention_policy(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get current data retention policies."""
    return get_retention_policy()


@router.get("/rgpd/compliance-status")
async def compliance_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get RGPD compliance checklist status."""
    return {
        "checklist": RGPD_CHECKLIST,
        "compliant_count": sum(1 for v in RGPD_CHECKLIST.values() if v["status"] == "COMPLIANT"),
        "total_count": len(RGPD_CHECKLIST),
    }
