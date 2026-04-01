from __future__ import annotations

import logging
import uuid

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.modal import EmployeeModal
from app.models.site import Site

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Weather impact configuration
# ---------------------------------------------------------------------------

_WEATHER_VULNERABILITY: dict[str, tuple[float, str]] = {
    "deux_roues_non_motorise": (0.85, "transport_public"),
    "auto_stop": (0.80, "transport_public"),
    "deux_roues_motorise": (0.45, "vehicule_particulier"),
    "covoiturage": (0.15, "vehicule_particulier"),
    "transport_public": (0.10, "vehicule_particulier"),
    "vehicule_particulier": (0.05, "covoiturage"),
    "navette_entreprise": (0.05, "vehicule_particulier"),
    "autre": (0.20, "transport_public"),
}

# ---------------------------------------------------------------------------
# Disruption vulnerability configuration
# ---------------------------------------------------------------------------

_DISRUPTION_CONFIG: dict[str, tuple[float, list[str]]] = {
    "transport_public": (80.0, ["strike", "service_interruption"]),
    "navette_entreprise": (70.0, ["company_downtime", "driver_absence"]),
    "covoiturage": (60.0, ["driver_absent", "schedule_change"]),
    "auto_stop": (50.0, ["weather", "safety_concern"]),
    "deux_roues_non_motorise": (40.0, ["weather", "infrastructure"]),
    "deux_roues_motorise": (30.0, ["weather", "road_conditions"]),
    "vehicule_particulier": (10.0, ["fuel_cost", "traffic"]),
    "autre": (20.0, ["availability"]),
}


# ---------------------------------------------------------------------------
# Weather-dependent modal analysis
# ---------------------------------------------------------------------------


async def analyze_weather_impact(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Analyze how many employees would switch modes in bad weather.

    Returns per-mode: employee_count, switch_probability, likely_alternative.
    """
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(EmployeeModal.primary_mode, func.count().label("cnt"))
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
        .group_by(EmployeeModal.primary_mode)
        .order_by(func.count().desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    impacts: list[dict] = []
    for row in rows:
        mode = row.primary_mode
        count = row.cnt
        probability, alternative = _WEATHER_VULNERABILITY.get(mode, (0.10, "autre"))
        impacts.append(
            {
                "mode": mode,
                "employee_count": count,
                "switch_probability": probability,
                "likely_alternative": alternative,
            }
        )

    return impacts


# ---------------------------------------------------------------------------
# Disruption vulnerability analysis
# ---------------------------------------------------------------------------


async def analyze_disruption_vulnerability(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Identify transport modes vulnerable to disruptions.

    Returns per-mode: employee_count, vulnerability_score, disruption_types.
    """
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(EmployeeModal.primary_mode, func.count().label("cnt"))
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
        .group_by(EmployeeModal.primary_mode)
        .order_by(func.count().desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    disruptions: list[dict] = []
    for row in rows:
        mode = row.primary_mode
        count = row.cnt
        vuln_score, d_types = _DISRUPTION_CONFIG.get(mode, (15.0, ["unknown"]))
        disruptions.append(
            {
                "mode": mode,
                "employee_count": count,
                "vulnerability_score": vuln_score,
                "disruption_types": d_types,
            }
        )

    return disruptions


# ---------------------------------------------------------------------------
# Carpool contribution potential
# ---------------------------------------------------------------------------


async def analyze_carpool_potential(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """Calculate carpool supply (volunteer seats) vs demand per site."""
    conditions = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    # Supply: volunteer drivers' available seats per site
    supply_stmt = (
        select(
            Employee.site_id,
            func.coalesce(func.sum(EmployeeModal.carpool_seats_available), 0).label(
                "supply"
            ),
        )
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions, EmployeeModal.volunteer_driver.is_(True))
        .group_by(Employee.site_id)
    )
    supply_result = await db.execute(supply_stmt)
    supply_map: dict[uuid.UUID, int] = {
        row.site_id: int(row.supply) for row in supply_result.all()
    }

    # Demand: employees interested in company transport without private car
    demand_stmt = (
        select(Employee.site_id, func.count().label("demand"))
        .join(EmployeeModal, EmployeeModal.employee_id == Employee.id)
        .where(
            *conditions,
            EmployeeModal.interest_company_transport == "Oui",
            EmployeeModal.has_private_car.is_(False),
        )
        .group_by(Employee.site_id)
    )
    demand_result = await db.execute(demand_stmt)
    demand_map: dict[uuid.UUID, int] = {
        row.site_id: int(row.demand) for row in demand_result.all()
    }

    # Merge and fetch site names
    all_site_ids = set(supply_map.keys()) | set(demand_map.keys())
    if not all_site_ids:
        return []

    site_stmt = select(Site.id, Site.name).where(Site.id.in_(all_site_ids))
    site_result = await db.execute(site_stmt)
    site_names: dict[uuid.UUID, str] = {
        row.id: row.name for row in site_result.all()
    }

    potentials: list[dict] = []
    for sid in all_site_ids:
        supply = supply_map.get(sid, 0)
        demand = demand_map.get(sid, 0)
        coverage = round(supply / demand, 2) if demand > 0 else 0.0
        potentials.append(
            {
                "site_id": str(sid),
                "site_name": site_names.get(sid, "Unknown"),
                "supply_seats": supply,
                "demand_count": demand,
                "coverage_ratio": coverage,
            }
        )

    return potentials
