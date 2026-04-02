from __future__ import annotations

import logging
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.optimization import Optimization
from app.models.scenario import Scenario

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONDITION_ALIAS_MAP: dict[str, str] = {
    "pluie": "rain",
    "greve_transport": "strike",
    "pic_activite": "peak",
    "nuit": "night",
    "defaillance_tc": "transit_failure",
}

DEFAULT_DEMAND_MULTIPLIERS: dict[str, float] = {
    "normal": 1.0,
    "rain": 1.15,
    "strike": 1.50,
    "peak": 1.30,
    "night": 0.80,
    "transit_failure": 1.40,
}

CONDITION_PARAM_ADJUSTMENTS: dict[str, dict] = {
    "normal": {},
    "rain": {"eps_meters": 700.0},
    "strike": {"eps_meters": 800.0, "max_cluster_size": 50},
    "peak": {"max_cluster_size": 60},
    "night": {"max_walking_distance_meters": 500.0},
    "transit_failure": {"eps_meters": 800.0},
}

# Fuel/CO2 constants (same as optimization pipeline)
FUEL_CONSUMPTION_L_PER_100KM = 15.0
FUEL_COST_MAD_PER_LITER = 12.0
CO2_KG_PER_LITER = 2.68


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def resolve_condition_type(raw: str) -> str:
    """Normalize French aliases to English canonical names."""
    key = raw.strip().lower()
    return CONDITION_ALIAS_MAP.get(key, key)


def get_demand_multiplier(
    condition_type: str, override: float | None = None
) -> float:
    """Return the demand multiplier for a condition type, or the override."""
    if override is not None:
        return override
    return DEFAULT_DEMAND_MULTIPLIERS.get(condition_type, 1.0)


def estimate_scenario_metrics(
    baseline_metrics: dict,
    demand_multiplier: float,
) -> dict:
    """Scale baseline optimization metrics by a demand multiplier.

    This is an approximation: actual results would require re-running the
    full optimization pipeline. Linear scaling is used for cost, distance,
    and fleet sizing.
    """
    total_employees = baseline_metrics.get("total_employees", 0)
    base_assigned = baseline_metrics.get("employees_assigned", 0)
    base_vehicles = baseline_metrics.get("total_vehicles_used", 0)
    base_clusters = baseline_metrics.get("total_clusters", 0)
    base_distance = baseline_metrics.get("total_distance_km", 0.0)
    base_duration = baseline_metrics.get("total_duration_minutes", 0.0)
    base_occupancy = baseline_metrics.get("avg_occupancy_rate", 0.0)

    # Scale employee demand (capped at total)
    scaled_assigned = min(
        math.ceil(base_assigned * demand_multiplier), total_employees
    ) if total_employees > 0 else 0

    # Scale fleet and clusters
    scaled_vehicles = math.ceil(base_vehicles * demand_multiplier)
    scaled_clusters = math.ceil(base_clusters * demand_multiplier)

    # Scale distance and duration
    scaled_distance = round(base_distance * demand_multiplier, 2)
    scaled_duration = round(base_duration * demand_multiplier, 2)

    # Recalculate fuel and emissions from scaled distance
    scaled_fuel = round(
        scaled_distance * FUEL_CONSUMPTION_L_PER_100KM / 100.0, 2
    )
    scaled_fuel_cost = round(scaled_fuel * FUEL_COST_MAD_PER_LITER, 2)
    scaled_co2 = round(scaled_fuel * CO2_KG_PER_LITER, 2)

    # Occupancy: keep baseline rate (it's an average per vehicle)
    scaled_occupancy = round(base_occupancy, 2)

    return {
        "total_employees": total_employees,
        "employees_assigned": scaled_assigned,
        "total_clusters": scaled_clusters,
        "total_vehicles_used": scaled_vehicles,
        "avg_occupancy_rate": scaled_occupancy,
        "total_distance_km": scaled_distance,
        "total_duration_minutes": scaled_duration,
        "estimated_fuel_liters": scaled_fuel,
        "estimated_fuel_cost_mad": scaled_fuel_cost,
        "co2_estimate_kg": scaled_co2,
        "demand_multiplier_applied": demand_multiplier,
    }


# ---------------------------------------------------------------------------
# Core service functions
# ---------------------------------------------------------------------------


async def get_latest_baseline(
    db: AsyncSession, tenant_id: uuid.UUID, site_id: uuid.UUID
) -> Optimization | None:
    """Find the latest completed optimization for a site."""
    stmt = (
        select(Optimization)
        .where(
            Optimization.tenant_id == tenant_id,
            Optimization.site_id == site_id,
            Optimization.status == "completed",
        )
        .order_by(Optimization.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def simulate_scenario(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    site_id: uuid.UUID,
    condition_type: str,
    demand_multiplier: float | None = None,
    custom_params: dict | None = None,
    name: str | None = None,
) -> Scenario:
    """Run a scenario simulation against the latest baseline optimization."""
    multiplier = get_demand_multiplier(condition_type, demand_multiplier)

    baseline = await get_latest_baseline(db, tenant_id, site_id)

    if baseline is None:
        # No baseline: create scenario with empty metrics and a warning
        estimated = estimate_scenario_metrics({}, multiplier)
        baseline_id = None
        logger.warning(
            "No completed optimization for site %s; scenario has empty baseline",
            site_id,
        )
    else:
        estimated = estimate_scenario_metrics(baseline.metrics, multiplier)
        baseline_id = baseline.id

    # Merge condition param adjustments with custom params
    params = dict(CONDITION_PARAM_ADJUSTMENTS.get(condition_type, {}))
    if custom_params:
        params.update(custom_params)

    scenario = Scenario(
        tenant_id=tenant_id,
        site_id=site_id,
        baseline_optimization_id=baseline_id,
        condition_type=condition_type,
        demand_multiplier=multiplier,
        custom_params=params,
        estimated_metrics=estimated,
        name=name,
    )
    db.add(scenario)
    await db.flush()
    return scenario


def compute_deltas(scenarios: list[Scenario]) -> list[dict]:
    """Compute pairwise metric deltas between scenarios."""
    deltas: list[dict] = []
    for i in range(len(scenarios)):
        for j in range(i + 1, len(scenarios)):
            a = scenarios[i].estimated_metrics
            b = scenarios[j].estimated_metrics
            deltas.append(
                {
                    "scenario_a_id": scenarios[i].id,
                    "scenario_b_id": scenarios[j].id,
                    "vehicles_delta": b.get("total_vehicles_used", 0)
                    - a.get("total_vehicles_used", 0),
                    "cost_delta_mad": round(
                        b.get("estimated_fuel_cost_mad", 0.0)
                        - a.get("estimated_fuel_cost_mad", 0.0),
                        2,
                    ),
                    "co2_delta_kg": round(
                        b.get("co2_estimate_kg", 0.0)
                        - a.get("co2_estimate_kg", 0.0),
                        2,
                    ),
                    "distance_delta_km": round(
                        b.get("total_distance_km", 0.0)
                        - a.get("total_distance_km", 0.0),
                        2,
                    ),
                    "duration_delta_minutes": round(
                        b.get("total_duration_minutes", 0.0)
                        - a.get("total_duration_minutes", 0.0),
                        2,
                    ),
                    "occupancy_delta_pct": round(
                        b.get("avg_occupancy_rate", 0.0)
                        - a.get("avg_occupancy_rate", 0.0),
                        2,
                    ),
                }
            )
    return deltas
