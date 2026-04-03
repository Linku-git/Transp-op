from __future__ import annotations

import logging
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.configuration_plan import ConfigurationPlan
from app.models.configuration_transport import ConfigurationTransport
from app.models.employee import Employee
from app.models.vehicle import Vehicle
from app.services.hr_analytics import compute_hr_kpis
from app.services.kpi_service import (
    KPI_TYPES,
    capture_all_sites_snapshots,
    capture_kpi_snapshot,
    get_kpi_trend,
)
from app.services.rse_analytics import compute_rse_kpis, generate_dpef_pdf

logger = logging.getLogger(__name__)

CAPACITY: dict[str, int] = {"AUTOCAR": 54, "MINIBUS": 25, "MINICAR": 12}
COST_PER_KM: dict[str, float] = {"AUTOCAR": 4.50, "MINIBUS": 3.20, "MINICAR": 2.50}
FUEL_RATE_DEFAULT = 4.50
AVG_CAR_KM_PER_DAY = 35
CO2_PER_CAR_KM = 0.12

router = APIRouter(prefix="/kpis")


@router.get("/dashboard", response_model=dict)
async def get_dashboard_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf", "manager")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return dashboard KPIs from real master data: parc véhicule, configuration transport, employees."""

    # ── 1. Total vehicles from parc véhicule ──────────────────────────────
    total_vehicles: int = await db.scalar(
        select(func.count(Vehicle.id)).where(Vehicle.tenant_id == current_user.tenant_id)
    ) or 0

    # ── 2. Total km from current active configuration plan ─────────────────
    total_km_raw = await db.scalar(
        select(func.coalesce(func.sum(ConfigurationTransport.km), 0))
        .join(ConfigurationPlan, ConfigurationTransport.plan_id == ConfigurationPlan.id)
        .where(
            ConfigurationPlan.tenant_id == current_user.tenant_id,
            ConfigurationPlan.is_active.is_(True),
        )
    )
    total_km: float = float(total_km_raw or 0)

    # ── 3. Vehicle type breakdown from active config (for capacity / cost) ─
    type_rows = (
        await db.execute(
            select(
                ConfigurationTransport.type_vehicule,
                func.count().label("cnt"),
            )
            .join(ConfigurationPlan, ConfigurationTransport.plan_id == ConfigurationPlan.id)
            .where(
                ConfigurationPlan.tenant_id == current_user.tenant_id,
                ConfigurationPlan.is_active.is_(True),
            )
            .group_by(ConfigurationTransport.type_vehicule)
        )
    ).all()

    total_circuits = sum(r.cnt for r in type_rows)
    total_seats = 0
    fuel_cost = 0.0
    for row in type_rows:
        vtype = (row.type_vehicule or "AUTOCAR").upper()
        cap = CAPACITY.get(vtype, 54)
        cpm = COST_PER_KM.get(vtype, FUEL_RATE_DEFAULT)
        total_seats += row.cnt * cap
        circuit_km = (total_km / total_circuits * row.cnt) if total_circuits else 0
        fuel_cost += circuit_km * cpm

    if not total_seats:
        total_seats = total_vehicles * 54
    if not fuel_cost:
        fuel_cost = total_km * FUEL_RATE_DEFAULT

    # ── 4. Employee modal split ────────────────────────────────────────────
    emp_row = (
        await db.execute(
            select(
                func.count(Employee.id).label("total"),
                func.sum(
                    case((Employee.current_transport_mode == "company_bus", 1), else_=0)
                ).label("bus_users"),
                func.sum(
                    case((Employee.current_transport_mode == "personal_car", 1), else_=0)
                ).label("car_users"),
            ).where(
                Employee.tenant_id == current_user.tenant_id,
                Employee.active.is_(True),
            )
        )
    ).first()

    total_emp: int = int(emp_row.total or 0)
    bus_users: int = int(emp_row.bus_users or 0)
    car_users: int = int(emp_row.car_users or 0)

    # ── 5. Avg occupancy = bus employees / total available seats ───────────
    avg_occupancy: float = round((bus_users / total_seats * 100) if total_seats else 0, 1)

    # ── 6. CO2 saved: each bus user not driving saves AVG_CAR_KM_PER_DAY km ─
    co2_saved_kg: float = round(bus_users * AVG_CAR_KM_PER_DAY * CO2_PER_CAR_KM, 0)

    logger.info(
        "Dashboard KPIs: vehicles=%d km=%.0f bus_users=%d occupancy=%.1f%%",
        total_vehicles, total_km, bus_users, avg_occupancy,
    )

    return {
        "total_vehicles": total_vehicles,
        "total_distance_km": total_km,
        "avg_occupancy_rate": avg_occupancy,
        "fuel_cost_mad": round(fuel_cost, 0),
        "co2_saved_kg": co2_saved_kg,
        "bus_users": bus_users,
        "car_users": car_users,
        "total_employees": total_emp,
        "total_circuits": total_circuits,
    }


@router.get("/hr", response_model=dict)
async def get_hr_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all HR dashboard KPIs: mobility coverage, absenteeism, retention, shadow zones."""
    result = await compute_hr_kpis(current_user.tenant_id, db)
    logger.info("HR KPIs computed for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return result


@router.get("/rse", response_model=dict)
async def get_rse_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all RSE (Corporate Social Responsibility) KPIs: CO2 savings, modal distribution, ZFE compliance."""
    result = await compute_rse_kpis(current_user.tenant_id, db)
    logger.info("RSE KPIs computed for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return result


@router.post("/rse/dpef")
async def export_dpef_report(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate and download a DPEF (Declaration de Performance Extra-Financiere) PDF report."""
    rse_data = await compute_rse_kpis(current_user.tenant_id, db)
    pdf_bytes = generate_dpef_pdf(rse_data)
    logger.info("DPEF report generated for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=rapport_dpef.pdf",
        },
    )


@router.post("/snapshot", response_model=dict)
async def create_kpi_snapshot(
    site_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Capture KPI snapshot for a site (or all sites if site_id is None)."""
    if site_id is not None:
        snapshots = await capture_kpi_snapshot(current_user.tenant_id, site_id, db)
        logger.info(
            "KPI snapshot captured for site %s by user %s",
            site_id,
            current_user.id,
        )
        return {
            "data": {
                "count": len(snapshots),
                "site_id": str(site_id),
                "kpi_types": [s.kpi_type for s in snapshots],
            }
        }
    else:
        count = await capture_all_sites_snapshots(current_user.tenant_id, db)
        logger.info(
            "KPI snapshots captured for all sites by user %s (%d total)",
            current_user.id,
            count,
        )
        return {
            "data": {
                "count": count,
                "site_id": None,
                "kpi_types": KPI_TYPES,
            }
        }


@router.get("/trend", response_model=dict)
async def get_kpi_trend_data(
    kpi_type: str = Query(...),
    site_id: uuid.UUID | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get historical KPI trend data for dashboard charts."""
    if kpi_type not in KPI_TYPES:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail=f"Invalid kpi_type '{kpi_type}'. Must be one of: {KPI_TYPES}",
        )

    parsed_start = date.fromisoformat(start_date) if start_date else None
    parsed_end = date.fromisoformat(end_date) if end_date else None

    trend = await get_kpi_trend(
        tenant_id=current_user.tenant_id,
        db=db,
        kpi_type=kpi_type,
        site_id=site_id,
        start_date=parsed_start,
        end_date=parsed_end,
    )
    logger.info(
        "KPI trend queried: type=%s site=%s range=%s..%s (%d points)",
        kpi_type,
        site_id,
        start_date,
        end_date,
        len(trend),
    )
    return {"data": trend}
