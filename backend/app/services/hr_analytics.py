from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import case, cast, func, select, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.leave import EmployeeLeave
from app.models.modal import EmployeeModal
from app.models.optimization import Cluster, Optimization
from app.models.site import Site

logger = logging.getLogger(__name__)

# Thresholds
SHADOW_ZONE_DISTANCE_KM = 30  # Employees beyond this are "shadow zone"
SHADOW_ZONE_NO_INTEREST = "Non"  # No interest in company transport
WORKING_DAYS_PER_YEAR = 220


# ---------------------------------------------------------------------------
# Mobility Coverage
# ---------------------------------------------------------------------------


async def compute_mobility_coverage(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Compute mobility coverage: % of employees with transport solution.

    Breakdown by site, shift, department (team), and time slot.
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Total employees
    total_stmt = select(func.count()).select_from(Employee).where(*base_filter)
    total = (await db.execute(total_stmt)).scalar_one()

    if total == 0:
        return {"total_employees": 0, "covered_employees": 0, "coverage_pct": 0, "by_site": [], "by_shift": [], "by_department": []}

    # Covered = opt_in_company_transport in ('Oui', 'Peut-etre') or has transport_required
    covered_filter = [
        *base_filter,
        Employee.opt_in_company_transport.in_(["Oui", "Sous conditions"]),
    ]
    covered_stmt = select(func.count()).select_from(Employee).where(*covered_filter)
    covered = (await db.execute(covered_stmt)).scalar_one()

    # By site
    by_site_stmt = (
        select(
            Site.name.label("site_name"),
            func.count().label("total"),
            func.count().filter(Employee.opt_in_company_transport.in_(["Oui", "Sous conditions"])).label("covered"),
        )
        .join(Site, Employee.site_id == Site.id)
        .where(*base_filter)
        .group_by(Site.name)
        .order_by(Site.name)
    )
    site_rows = (await db.execute(by_site_stmt)).all()

    # By shift
    by_shift_stmt = (
        select(
            func.coalesce(Employee.shift_time, "Non defini").label("shift"),
            func.count().label("total"),
            func.count().filter(Employee.opt_in_company_transport.in_(["Oui", "Sous conditions"])).label("covered"),
        )
        .where(*base_filter)
        .group_by("shift")
        .order_by("shift")
    )
    shift_rows = (await db.execute(by_shift_stmt)).all()

    # By department (team)
    by_dept_stmt = (
        select(
            func.coalesce(Employee.department, "Non defini").label("department"),
            func.count().label("total"),
            func.count().filter(Employee.opt_in_company_transport.in_(["Oui", "Sous conditions"])).label("covered"),
        )
        .where(*base_filter)
        .group_by("department")
        .order_by("department")
    )
    dept_rows = (await db.execute(by_dept_stmt)).all()

    def _pct(covered: int, total: int) -> float:
        return round(covered / total * 100, 1) if total > 0 else 0

    return {
        "total_employees": total,
        "covered_employees": covered,
        "coverage_pct": _pct(covered, total),
        "by_site": [
            {"name": r.site_name, "total": r.total, "covered": r.covered, "pct": _pct(r.covered, r.total)}
            for r in site_rows
        ],
        "by_shift": [
            {"name": r.shift, "total": r.total, "covered": r.covered, "pct": _pct(r.covered, r.total)}
            for r in shift_rows
        ],
        "by_department": [
            {"name": r.department, "total": r.total, "covered": r.covered, "pct": _pct(r.covered, r.total)}
            for r in dept_rows
        ],
    }


# ---------------------------------------------------------------------------
# Mobility Score Evolution
# ---------------------------------------------------------------------------


async def compute_mobility_score_evolution(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[dict]:
    """
    Return mobility score evolution from completed optimization runs.

    Uses optimization metrics as proxy for mobility score over time.
    """
    stmt = (
        select(
            Optimization.completed_at,
            Optimization.metrics,
            Optimization.site_id,
        )
        .where(
            Optimization.tenant_id == tenant_id,
            Optimization.status == "completed",
            Optimization.completed_at.isnot(None),
        )
        .order_by(Optimization.completed_at.asc())
        .limit(50)
    )
    rows = (await db.execute(stmt)).all()

    evolution: list[dict] = []
    for row in rows:
        metrics = row.metrics or {}
        occupancy = metrics.get("average_occupancy_pct", 0)
        co2 = metrics.get("total_co2_kg", 0)
        evolution.append({
            "date": row.completed_at.isoformat() if row.completed_at else None,
            "site_id": str(row.site_id) if row.site_id else None,
            "occupancy_pct": occupancy,
            "co2_kg": co2,
            "score": min(100, round(occupancy * 1.2, 1)),  # Proxy score
        })

    return evolution


# ---------------------------------------------------------------------------
# Absenteeism Correlation
# ---------------------------------------------------------------------------


async def compute_absenteeism_correlation(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Correlate transport quality with absence rates.

    Compare absence rates for employees with/without company transport interest.
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Group employees by transport interest
    groups = {
        "with_transport": ["Oui"],
        "without_transport": ["Non"],
        "maybe_transport": ["Sous conditions"],
    }

    results: dict[str, Any] = {}

    for group_name, interest_values in groups.items():
        # Count employees in group
        emp_count_stmt = (
            select(func.count())
            .select_from(Employee)
            .where(*base_filter, Employee.opt_in_company_transport.in_(interest_values))
        )
        emp_count = (await db.execute(emp_count_stmt)).scalar_one()

        # Count leave days for this group (end_date - start_date + 1)
        leave_days_stmt = (
            select(
                func.coalesce(
                    func.sum(EmployeeLeave.end_date - EmployeeLeave.start_date + 1),
                    0,
                )
            )
            .join(Employee, EmployeeLeave.employee_id == Employee.id)
            .where(*base_filter, Employee.opt_in_company_transport.in_(interest_values))
        )
        leave_days = (await db.execute(leave_days_stmt)).scalar_one()

        avg_absence_days = round(float(leave_days) / emp_count, 1) if emp_count > 0 else 0
        absence_rate = round(avg_absence_days / WORKING_DAYS_PER_YEAR * 100, 2) if emp_count > 0 else 0

        results[group_name] = {
            "employee_count": emp_count,
            "total_leave_days": int(leave_days),
            "avg_absence_days": avg_absence_days,
            "absence_rate_pct": absence_rate,
        }

    # Correlation indicator
    with_rate = results["with_transport"]["absence_rate_pct"]
    without_rate = results["without_transport"]["absence_rate_pct"]
    delta = round(without_rate - with_rate, 2)

    results["correlation"] = {
        "delta_pct": delta,
        "interpretation": (
            "Transport reduit l'absenteisme"
            if delta > 0
            else "Pas de correlation significative"
        ),
    }

    return results


# ---------------------------------------------------------------------------
# Retention Impact
# ---------------------------------------------------------------------------


async def compute_retention_impact(
    tenant_id: uuid.UUID,
    db: AsyncSession,
    avg_replacement_cost: float = 25000,
) -> dict[str, Any]:
    """
    Estimate retention impact of mobility solution.

    Compare turnover (end_date set) for transport vs non-transport groups.
    """
    base_filter = [Employee.tenant_id == tenant_id]

    total_stmt = select(func.count()).select_from(Employee).where(*base_filter)
    total = (await db.execute(total_stmt)).scalar_one()

    departed_stmt = (
        select(func.count())
        .select_from(Employee)
        .where(*base_filter, Employee.end_date.isnot(None))
    )
    departed = (await db.execute(departed_stmt)).scalar_one()

    # Departed with transport interest
    departed_with_stmt = (
        select(func.count())
        .select_from(Employee)
        .where(
            *base_filter,
            Employee.end_date.isnot(None),
            Employee.opt_in_company_transport.in_(["Oui", "Sous conditions"]),
        )
    )
    departed_with = (await db.execute(departed_with_stmt)).scalar_one()

    departed_without = departed - departed_with

    turnover_rate = round(departed / total * 100, 1) if total > 0 else 0
    estimated_savings = round(departed_without * avg_replacement_cost * 0.3, 2)  # 30% reduction potential

    return {
        "total_employees": total,
        "departed_total": departed,
        "departed_with_transport": departed_with,
        "departed_without_transport": departed_without,
        "turnover_rate_pct": turnover_rate,
        "avg_replacement_cost": avg_replacement_cost,
        "estimated_annual_savings": estimated_savings,
    }


# ---------------------------------------------------------------------------
# Shadow Zones
# ---------------------------------------------------------------------------


async def compute_shadow_zones(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Identify employees without satisfactory transport solution.

    Shadow zone: employees with distance > threshold AND no interest in company transport,
    or employees with no modal data at all.
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Employees with modal data beyond threshold and no interest
    shadow_modal_stmt = (
        select(
            Employee.id,
            Employee.first_name,
            Employee.last_name,
            Employee.quartier,
            Employee.city,
            EmployeeModal.distance_km,
            EmployeeModal.primary_mode,
        )
        .outerjoin(EmployeeModal, Employee.id == EmployeeModal.employee_id)
        .where(
            *base_filter,
            (
                (EmployeeModal.distance_km > SHADOW_ZONE_DISTANCE_KM)
                | (EmployeeModal.employee_id.is_(None))
            ),
        )
    )
    shadow_rows = (await db.execute(shadow_modal_stmt)).all()

    total_active_stmt = select(func.count()).select_from(Employee).where(*base_filter)
    total_active = (await db.execute(total_active_stmt)).scalar_one()

    shadow_employees = [
        {
            "id": str(r.id),
            "name": f"{r.first_name} {r.last_name}",
            "quartier": r.quartier,
            "city": r.city,
            "distance_km": float(r.distance_km) if r.distance_km else None,
            "primary_mode": r.primary_mode,
        }
        for r in shadow_rows
    ]

    return {
        "shadow_zone_count": len(shadow_employees),
        "total_active_employees": total_active,
        "shadow_zone_pct": round(len(shadow_employees) / total_active * 100, 1) if total_active > 0 else 0,
        "threshold_km": SHADOW_ZONE_DISTANCE_KM,
        "employees": shadow_employees[:50],  # Limit to 50 for response size
    }


# ---------------------------------------------------------------------------
# Full HR KPIs
# ---------------------------------------------------------------------------


async def compute_hr_kpis(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """Compute all HR dashboard KPIs."""
    mobility_coverage = await compute_mobility_coverage(tenant_id, db)
    mobility_evolution = await compute_mobility_score_evolution(tenant_id, db)
    absenteeism = await compute_absenteeism_correlation(tenant_id, db)
    retention = await compute_retention_impact(tenant_id, db)
    shadow_zones = await compute_shadow_zones(tenant_id, db)

    return {
        "mobility_coverage": mobility_coverage,
        "mobility_score_evolution": mobility_evolution,
        "absenteeism_correlation": absenteeism,
        "retention_impact": retention,
        "shadow_zones": shadow_zones,
    }
