from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee

logger = logging.getLogger(__name__)

# Shift-time to departure-time-slot mapping
_SHIFT_TO_SLOT: dict[str, str] = {
    "P1": "morning",    # 06:00-09:00
    "P2": "afternoon",  # 12:00-15:00
    "P3": "evening",    # 15:00-19:00
    "N":  "night",      # 19:00-24:00
    "S":  "morning",    # split / standard → morning
}

_TIME_SLOTS = ["morning", "midday", "afternoon", "evening", "night"]


# ---------------------------------------------------------------------------
# Per-employee mobility score (based on Employee fields)
# ---------------------------------------------------------------------------

def calculate_employee_score(emp: Employee) -> tuple[float, dict[str, float]]:
    """Calculate a mobility score (0-100) for a single employee.

    Higher score = better mobility situation.
    Returns ``(score, factors_breakdown)``.
    """
    score = 0.0
    factors: dict[str, float] = {}

    # Interest in company transport
    if emp.opt_in_company_transport == "Oui":
        score += 20.0
        factors["company_transport_interest"] = 20.0

    # Has private car (backup option available)
    if emp.has_private_car:
        score += 5.0
        factors["has_private_car"] = 5.0

    # Current transport mode bonus
    mode = emp.current_transport_mode or ""
    if mode == "company_bus":
        score += 25.0
        factors["company_shuttle"] = 25.0
    elif mode == "walk":
        score += 20.0
        factors["sustainable_mode_walk"] = 20.0
    elif mode in ("motorcycle",):
        score += 10.0
        factors["sustainable_mode_motor"] = 10.0
    elif mode == "personal_car":
        score += 5.0
        factors["personal_car"] = 5.0
    elif mode == "taxi":
        score += 2.0
        factors["taxi"] = 2.0

    # Clamp 0-100
    score = max(0.0, min(100.0, score))
    return score, factors


# ---------------------------------------------------------------------------
# Group score aggregation
# ---------------------------------------------------------------------------


async def calculate_group_scores(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Calculate average mobility scores grouped by site, department, shift.

    Returns a flat list of ``{group_type, group_key, group_label, avg_score, employee_count}``.
    """
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(Employee)
        .options(selectinload(Employee.site))
        .where(*conditions)
    )
    result = await db.execute(stmt)
    employees = list(result.scalars().all())

    employee_scores: list[dict] = []
    for emp in employees:
        sc, _ = calculate_employee_score(emp)
        employee_scores.append(
            {
                "score": sc,
                "site_id": str(emp.site_id) if emp.site_id else "unknown",
                "site_name": emp.site.name if emp.site else "Unknown",
                "department": emp.department or "unassigned",
                "shift": emp.shift_time or "unassigned",
            }
        )

    groups: list[dict] = []

    # Group by site
    by_site: dict[str, list[float]] = {}
    site_labels: dict[str, str] = {}
    for es in employee_scores:
        key = es["site_id"]
        by_site.setdefault(key, []).append(es["score"])
        site_labels[key] = es["site_name"]
    for key, scores in by_site.items():
        groups.append(
            {
                "group_type": "site",
                "group_key": key,
                "group_label": site_labels[key],
                "avg_score": round(sum(scores) / len(scores), 2),
                "employee_count": len(scores),
            }
        )

    # Group by department
    by_dept: dict[str, list[float]] = {}
    for es in employee_scores:
        key = es["department"]
        by_dept.setdefault(key, []).append(es["score"])
    for key, scores in by_dept.items():
        groups.append(
            {
                "group_type": "department",
                "group_key": key,
                "group_label": key,
                "avg_score": round(sum(scores) / len(scores), 2),
                "employee_count": len(scores),
            }
        )

    # Group by shift
    by_shift: dict[str, list[float]] = {}
    for es in employee_scores:
        key = es["shift"]
        by_shift.setdefault(key, []).append(es["score"])
    for key, scores in by_shift.items():
        groups.append(
            {
                "group_type": "shift",
                "group_key": key,
                "group_label": key,
                "avg_score": round(sum(scores) / len(scores), 2),
                "employee_count": len(scores),
            }
        )

    return groups


# ---------------------------------------------------------------------------
# Time-slot score (derived from shift_time)
# ---------------------------------------------------------------------------


async def calculate_timeslot_scores(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Count employees per departure-time bucket, derived from shift_time."""
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = select(Employee.shift_time).where(*conditions)
    result = await db.execute(stmt)
    rows = result.all()

    buckets: dict[str, int] = {slot: 0 for slot in _TIME_SLOTS}
    buckets["unknown"] = 0

    for (shift,) in rows:
        slot = _SHIFT_TO_SLOT.get(shift or "", "unknown")
        buckets[slot] += 1

    return [{"slot": slot, "count": count} for slot, count in buckets.items()]


# ---------------------------------------------------------------------------
# Shadow zone identification
# ---------------------------------------------------------------------------


async def identify_shadow_zones(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    distance_threshold_km: float = 30.0,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Find employees with no satisfactory transport solution.

    Criteria: car-dependent (personal_car mode) AND not interested in company transport.
    """
    conditions = [
        Employee.tenant_id == tenant_id,
        Employee.active.is_(True),
        Employee.current_transport_mode == "personal_car",
        Employee.opt_in_company_transport != "Oui",
    ]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(Employee)
        .options(selectinload(Employee.site))
        .where(*conditions)
    )
    result = await db.execute(stmt)
    employees = list(result.scalars().all())

    shadow_employees: list[dict] = []
    for emp in employees:
        shadow_employees.append(
            {
                "employee_id": str(emp.id),
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "lat": emp.lat,
                "lng": emp.lng,
                "site_id": str(emp.site_id),
                "distance_km": None,
                "reason": (
                    f"Car-dependent, not interested in company transport "
                    f"(opt_in={emp.opt_in_company_transport})"
                ),
            }
        )

    logger.info(
        "Shadow zone analysis: %d employees identified for tenant %s",
        len(shadow_employees),
        tenant_id,
    )
    return shadow_employees
