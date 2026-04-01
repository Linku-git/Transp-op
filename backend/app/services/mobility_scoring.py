from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.modal import EmployeeModal

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-employee mobility score
# ---------------------------------------------------------------------------


def calculate_employee_score(modal: EmployeeModal) -> tuple[float, dict[str, float]]:
    """Calculate a mobility score (0-100) for a single employee.

    Higher score = better mobility situation (more flexible, more options).
    Returns ``(score, factors_breakdown)``.
    """
    score = 0.0
    factors: dict[str, float] = {}

    # Distance factor
    if modal.distance_km is not None:
        distance = float(modal.distance_km)
        if distance < 10:
            score += 15.0
            factors["distance_short"] = 15.0
        elif distance < 20:
            score += 5.0
            factors["distance_medium"] = 5.0
        elif distance < 30:
            score -= 5.0
            factors["distance_long"] = -5.0
        else:
            score -= 15.0
            factors["distance_very_long"] = -15.0

    # Interest in company transport
    if modal.interest_company_transport == "Oui":
        score += 20.0
        factors["company_transport_interest"] = 20.0
    elif modal.interest_company_transport == "Sous conditions":
        score += 10.0
        factors["company_transport_conditional"] = 10.0

    # Pickup flexibility
    if modal.accepts_common_pickup:
        score += 10.0
        factors["accepts_common_pickup"] = 10.0

    # Volunteer driver
    if modal.volunteer_driver:
        score += 15.0
        factors["volunteer_driver"] = 15.0

    # Has private car (has backup option)
    if modal.has_private_car:
        score += 5.0
        factors["has_private_car"] = 5.0

    # Alternative mode available
    if modal.alternative_mode is not None:
        score += 5.0
        factors["alternative_mode"] = 5.0

    # Primary mode bonus
    if modal.primary_mode in ("transport_public", "covoiturage"):
        score += 10.0
        factors["sustainable_mode"] = 10.0
    elif modal.primary_mode == "navette_entreprise":
        score += 15.0
        factors["company_shuttle"] = 15.0

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
        select(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .options(selectinload(EmployeeModal.employee))
        .where(*conditions)
    )
    result = await db.execute(stmt)
    modals = list(result.scalars().all())

    # Build per-employee scores
    employee_scores: list[dict] = []
    for modal in modals:
        sc, _ = calculate_employee_score(modal)
        emp = modal.employee
        employee_scores.append(
            {
                "score": sc,
                "site_id": str(emp.site_id) if emp else "unknown",
                "site_name": emp.site.name if emp and emp.site else "Unknown",
                "department": emp.department or "unassigned" if emp else "unknown",
                "shift": emp.shift_time or "unassigned" if emp else "unknown",
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
# Time-slot score
# ---------------------------------------------------------------------------

_TIME_SLOTS = [
    ("morning", 6, 9),
    ("midday", 9, 12),
    ("afternoon", 12, 15),
    ("evening", 15, 19),
    ("night", 19, 24),
]


async def calculate_timeslot_scores(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Count employees per departure-time bucket."""
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(EmployeeModal.departure_time)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
    )
    result = await db.execute(stmt)
    rows = result.all()

    buckets: dict[str, int] = {slot: 0 for slot, _, _ in _TIME_SLOTS}
    buckets["unknown"] = 0

    for (dep_time,) in rows:
        if dep_time is None:
            buckets["unknown"] += 1
            continue
        hour = dep_time.hour
        placed = False
        for slot_name, start, end in _TIME_SLOTS:
            if start <= hour < end:
                buckets[slot_name] += 1
                placed = True
                break
        if not placed:
            buckets["unknown"] += 1

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

    Criteria: distance > threshold AND interest != 'Oui' AND car-dependent.
    """
    conditions = [
        Employee.tenant_id == tenant_id,
        Employee.active.is_(True),
        EmployeeModal.distance_km > Decimal(str(distance_threshold_km)),
        EmployeeModal.interest_company_transport != "Oui",
        EmployeeModal.primary_mode == "vehicule_particulier",
    ]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .options(selectinload(EmployeeModal.employee))
        .where(*conditions)
    )
    result = await db.execute(stmt)
    modals = list(result.scalars().all())

    shadow_employees: list[dict] = []
    for modal in modals:
        emp = modal.employee
        if emp is None:
            continue
        distance = float(modal.distance_km) if modal.distance_km else 0.0
        shadow_employees.append(
            {
                "employee_id": str(emp.id),
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "lat": emp.lat,
                "lng": emp.lng,
                "site_id": str(emp.site_id),
                "distance_km": distance,
                "reason": (
                    f"Car-dependent, {distance:.1f}km from site, "
                    f"no interest in company transport"
                ),
            }
        )

    logger.info(
        "Shadow zone analysis: %d employees identified for tenant %s",
        len(shadow_employees),
        tenant_id,
    )
    return shadow_employees
