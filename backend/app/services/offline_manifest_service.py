from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.site import Site
from app.models.point_arret import PointArret
from app.services.trip_booking_service import get_upcoming_trips


async def generate_offline_manifest(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    employee_id: uuid.UUID | None = None,
) -> dict:
    profile = None
    site = None
    point_arrets: list = []
    upcoming_trips: list = []

    # Get employee profile
    if employee_id:
        result = await db.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.tenant_id == tenant_id,
            )
        )
        emp = result.scalar_one_or_none()
        if emp:
            profile = {
                "id": str(emp.id),
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "email": getattr(emp, "email", None),
                "site_id": str(emp.site_id) if emp.site_id else None,
            }

            # Get site
            if emp.site_id:
                site_result = await db.execute(
                    select(Site).where(Site.id == emp.site_id)
                )
                site_obj = site_result.scalar_one_or_none()
                if site_obj:
                    site = {
                        "id": str(site_obj.id),
                        "name": site_obj.name,
                        "address": getattr(site_obj, "address", None),
                    }

            # Get pickup points for site
            if emp.site_id:
                pa_result = await db.execute(
                    select(PointArret).where(
                        PointArret.tenant_id == tenant_id,
                    )
                )
                point_arrets = [
                    {"id": str(pa.id), "name": pa.name}
                    for pa in pa_result.scalars().all()
                ]

        # Get upcoming trips
        trips = await get_upcoming_trips(db, tenant_id, employee_id)
        upcoming_trips = [
            {
                "id": str(t.id),
                "departure_time": t.departure_time.isoformat(),
                "status": t.status,
            }
            for t in trips
        ]

    return {
        "profile": profile,
        "upcoming_trips": upcoming_trips,
        "site": site,
        "point_arrets": point_arrets,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
