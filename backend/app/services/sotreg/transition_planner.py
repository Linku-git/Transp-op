from __future__ import annotations

import logging
import math
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_dec(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# Technology wave definitions
# ---------------------------------------------------------------------------

TECHNOLOGY_WAVES: dict[str, dict] = {
    "pilot": {"pct_fleet": 0.10, "description": "Phase pilote (10% de la flotte)"},
    "scale": {"pct_fleet": 0.40, "description": "Montee en charge (40% de la flotte)"},
    "full":  {"pct_fleet": 0.50, "description": "Deploiement complet (50% restant)"},
}

# Scenario pace (years per wave)
SCENARIO_PACE: dict[str, dict[str, int]] = {
    "aggressive":   {"pilot": 1, "scale": 2, "full": 2},   # 5 years total
    "moderate":     {"pilot": 2, "scale": 3, "full": 3},   # 8 years total
    "conservative": {"pilot": 2, "scale": 4, "full": 4},   # 10 years total
}

# Cost defaults (MAD)
DEFAULT_VEHICLE_COST_MAD: float = 300_000.0   # per electric vehicle
DEFAULT_IRVE_COST_PER_VEHICLE_MAD: float = 90_000.0  # charger + installation


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def validate_plan_inputs(
    fleet_size: int,
    total_budget_mad: float,
    start_year: int,
    scenario_type: str,
) -> dict:
    """Validate plan inputs.

    Checks:
    - ``fleet_size`` > 0
    - ``total_budget_mad`` > 0
    - ``start_year`` >= 2024
    - ``scenario_type`` is one of the recognised scenario keys

    Returns:
        Dict with ``valid`` (bool) and ``errors`` (list of str).
    """
    errors: list[str] = []

    if fleet_size <= 0:
        errors.append(
            f"fleet_size must be positive, got {fleet_size}"
        )

    if total_budget_mad <= 0:
        errors.append(
            f"total_budget_mad must be positive, got {total_budget_mad}"
        )

    if start_year < 2024:
        errors.append(
            f"start_year must be >= 2024, got {start_year}"
        )

    valid_scenarios = list(SCENARIO_PACE.keys())
    if scenario_type not in valid_scenarios:
        errors.append(
            f"scenario_type must be one of {valid_scenarios}, "
            f"got '{scenario_type}'"
        )

    return {"valid": len(errors) == 0, "errors": errors}


# ---------------------------------------------------------------------------
# Phase milestone computation
# ---------------------------------------------------------------------------


def compute_phase_milestones(
    phases: list[dict],
    fleet_size: int,
) -> list[dict]:
    """Compute milestones from a phase sequence.

    Each milestone marks the end of a phase and indicates the cumulative
    percentage of the fleet converted to electric at that point.

    Args:
        phases: List of phase dicts (as produced by ``generate_transition_plan``).
        fleet_size: Total fleet size (for percentage computation).

    Returns:
        List of milestone dicts, each with:
        - ``year`` -- the end year of the phase
        - ``description`` -- human-readable milestone text
        - ``target_pct`` -- cumulative % of fleet converted
        - ``vehicles_converted_cumulative`` -- cumulative vehicle count
    """
    if not phases or fleet_size <= 0:
        return []

    milestones: list[dict] = []
    cumulative_vehicles = 0

    for phase in phases:
        cumulative_vehicles += phase.get("vehicles_to_convert", 0)
        target_pct = round(cumulative_vehicles / fleet_size * 100, 2) if fleet_size > 0 else 0.0

        milestones.append({
            "year": phase["end_year"],
            "description": (
                f"Fin {phase['name']}: {cumulative_vehicles}/{fleet_size} "
                f"vehicules electriques ({target_pct}%)"
            ),
            "target_pct": target_pct,
            "vehicles_converted_cumulative": cumulative_vehicles,
        })

    return milestones


# ---------------------------------------------------------------------------
# Plan progress tracking
# ---------------------------------------------------------------------------


def compute_plan_progress(
    phases: list[dict],
    current_year: int = 2026,
) -> dict:
    """Track actual vs planned progress for a transition plan.

    Evaluates which phases are complete, in-progress, or pending based on
    ``current_year`` compared to each phase's ``start_year`` and ``end_year``.

    Args:
        phases: List of phase dicts (as produced by ``generate_transition_plan``).
        current_year: The reference year to evaluate progress against.

    Returns:
        Dict with:
        - ``pct_complete`` -- estimated overall completion percentage
        - ``current_phase`` -- name of the phase currently in progress (or None)
        - ``phases_completed`` -- number of fully completed phases
        - ``phases_remaining`` -- number of phases not yet started
        - ``budget_spent_mad`` -- total budget of completed phases
        - ``budget_remaining_mad`` -- total budget of incomplete phases
        - ``on_track`` -- True if current progress is on or ahead of schedule
    """
    if not phases:
        return {
            "pct_complete": 0.0,
            "current_phase": None,
            "phases_completed": 0,
            "phases_remaining": 0,
            "budget_spent_mad": 0.0,
            "budget_remaining_mad": 0.0,
            "on_track": True,
        }

    phases_completed = 0
    phases_remaining = 0
    current_phase_name: str | None = None
    budget_spent = Decimal("0")
    budget_remaining = Decimal("0")
    total_vehicles = 0
    vehicles_done = 0

    for phase in phases:
        phase_budget = _to_dec(phase.get("budget_allocated_mad", 0))
        phase_vehicles = phase.get("vehicles_to_convert", 0)
        total_vehicles += phase_vehicles

        if current_year >= phase["end_year"]:
            # Phase fully completed
            phases_completed += 1
            budget_spent += phase_budget
            vehicles_done += phase_vehicles
        elif current_year >= phase["start_year"]:
            # Phase in progress
            current_phase_name = phase["name"]
            # Estimate partial progress within this phase
            duration = phase["end_year"] - phase["start_year"]
            if duration > 0:
                years_in = current_year - phase["start_year"]
                partial_fraction = min(years_in / duration, 1.0)
                partial_vehicles = int(phase_vehicles * partial_fraction)
                vehicles_done += partial_vehicles
                partial_budget = _q(phase_budget * _to_dec(partial_fraction))
                budget_spent += partial_budget
                budget_remaining += phase_budget - partial_budget
            else:
                # Duration of zero means single-year phase; count as done
                # if current_year == start_year == end_year
                vehicles_done += phase_vehicles
                budget_spent += phase_budget
        else:
            # Phase not yet started
            phases_remaining += 1
            budget_remaining += phase_budget

    pct_complete = round(vehicles_done / total_vehicles * 100, 2) if total_vehicles > 0 else 0.0

    # Determine expected progress percentage based on timeline
    first_start = phases[0]["start_year"]
    last_end = phases[-1]["end_year"]
    total_duration = last_end - first_start
    if total_duration > 0:
        elapsed = max(0, min(current_year - first_start, total_duration))
        expected_pct = elapsed / total_duration * 100
    else:
        expected_pct = 100.0 if current_year >= first_start else 0.0

    on_track = pct_complete >= expected_pct * 0.9  # 10% tolerance

    return {
        "pct_complete": pct_complete,
        "current_phase": current_phase_name,
        "phases_completed": phases_completed,
        "phases_remaining": phases_remaining,
        "budget_spent_mad": float(_q(budget_spent)),
        "budget_remaining_mad": float(_q(budget_remaining)),
        "on_track": on_track,
    }


# ---------------------------------------------------------------------------
# Main transition plan generator
# ---------------------------------------------------------------------------


def generate_transition_plan(
    fleet_size: int,
    total_budget_mad: float,
    start_year: int = 2026,
    scenario_type: str = "moderate",
    vehicle_unit_cost_mad: float = DEFAULT_VEHICLE_COST_MAD,
    irve_cost_per_vehicle_mad: float = DEFAULT_IRVE_COST_PER_VEHICLE_MAD,
    currency: str = "MAD",
) -> dict:
    """Generate a phased electrification transition plan.

    Creates 3 phases (pilot / scale / full) distributed according to
    ``scenario_type`` pace.  Each phase specifies the number of vehicles
    to convert, budget allocation, timeline, and milestones.

    Budget allocation per phase::

        CAPEX_phase = vehicles_in_phase * (vehicle_unit_cost + irve_cost_per_vehicle)

    If ``total_budget_mad`` is insufficient to cover all phases, later
    phases are trimmed.  If the budget cannot cover even a single vehicle,
    the plan is returned with zero conversions and a deficit flag.

    Args:
        fleet_size: Total fleet size (number of vehicles).
        total_budget_mad: Available budget in MAD.
        start_year: First year of the transition plan.
        scenario_type: Pacing scenario -- ``aggressive``, ``moderate``,
            or ``conservative``.
        vehicle_unit_cost_mad: Cost per electric vehicle (MAD).
        irve_cost_per_vehicle_mad: IRVE infrastructure cost per vehicle (MAD).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``plan_name`` -- descriptive plan name
        - ``scenario_type`` -- the chosen scenario
        - ``fleet_size`` -- input fleet size
        - ``total_budget_mad`` -- input budget
        - ``phases`` -- list of phase dicts, each with:
            - ``name``, ``technology_wave``, ``description``
            - ``start_year``, ``end_year``, ``duration_years``
            - ``vehicles_to_convert``, ``target_pct_electric``
            - ``budget_allocated_mad``, ``vehicle_cost_mad``,
              ``infrastructure_cost_mad``
            - ``status`` -- ``"planned"``
        - ``total_phases`` -- number of phases
        - ``total_vehicles_converted`` -- sum across all phases
        - ``total_cost_mad`` -- total budget consumed
        - ``budget_surplus_or_deficit_mad`` -- positive = surplus, negative = deficit
        - ``milestones`` -- computed milestone list
        - ``currency``

    Raises:
        ValueError: If input validation fails.
    """
    # ---- Validate inputs --------------------------------------------------
    validation = validate_plan_inputs(
        fleet_size=fleet_size,
        total_budget_mad=total_budget_mad,
        start_year=start_year,
        scenario_type=scenario_type,
    )
    if not validation["valid"]:
        raise ValueError(
            f"Invalid plan inputs: {'; '.join(validation['errors'])}"
        )

    # ---- Decimal setup ----------------------------------------------------
    budget_remaining = _to_dec(total_budget_mad)
    unit_cost = _to_dec(vehicle_unit_cost_mad) + _to_dec(irve_cost_per_vehicle_mad)
    pace = SCENARIO_PACE[scenario_type]
    wave_order = ["pilot", "scale", "full"]

    # ---- Edge case: budget too small for even 1 vehicle -------------------
    if unit_cost > Decimal("0") and budget_remaining < unit_cost:
        logger.warning(
            "Budget %s %s insufficient for a single vehicle "
            "(unit cost = %s %s)",
            total_budget_mad,
            currency,
            float(unit_cost),
            currency,
        )
        empty_phases: list[dict] = []
        phase_start = start_year
        for wave_key in wave_order:
            wave = TECHNOLOGY_WAVES[wave_key]
            duration = pace[wave_key]
            phase_end = phase_start + duration

            empty_phases.append({
                "name": wave_key,
                "technology_wave": wave_key,
                "description": wave["description"],
                "start_year": phase_start,
                "end_year": phase_end,
                "duration_years": duration,
                "vehicles_to_convert": 0,
                "target_pct_electric": 0.0,
                "budget_allocated_mad": 0.0,
                "vehicle_cost_mad": 0.0,
                "infrastructure_cost_mad": 0.0,
                "status": "planned",
            })
            phase_start = phase_end

        return {
            "plan_name": f"Plan electrification {scenario_type} ({start_year})",
            "scenario_type": scenario_type,
            "fleet_size": fleet_size,
            "total_budget_mad": total_budget_mad,
            "phases": empty_phases,
            "total_phases": len(empty_phases),
            "total_vehicles_converted": 0,
            "total_cost_mad": 0.0,
            "budget_surplus_or_deficit_mad": float(_q(-unit_cost + budget_remaining)),
            "milestones": [],
            "currency": currency,
        }

    # ---- Build phases -----------------------------------------------------
    phases: list[dict] = []
    phase_start = start_year
    total_vehicles_converted = 0
    total_cost = Decimal("0")
    cumulative_pct = Decimal("0")

    for wave_key in wave_order:
        wave = TECHNOLOGY_WAVES[wave_key]
        duration = pace[wave_key]
        phase_end = phase_start + duration

        # Target vehicle count for this wave
        target_vehicles = max(1, math.ceil(fleet_size * wave["pct_fleet"]))

        # Ensure we do not exceed fleet_size in total
        remaining_fleet = fleet_size - total_vehicles_converted
        if target_vehicles > remaining_fleet:
            target_vehicles = remaining_fleet

        # Budget constraint: how many can we actually afford?
        if unit_cost > Decimal("0"):
            affordable = int(budget_remaining / unit_cost)
        else:
            # Zero cost per vehicle: all vehicles are affordable
            affordable = target_vehicles

        actual_vehicles = min(target_vehicles, affordable)

        # For fleet_size == 1: ensure the pilot gets the single vehicle
        if actual_vehicles <= 0:
            actual_vehicles = 0

        phase_vehicle_cost = _q(_to_dec(actual_vehicles) * _to_dec(vehicle_unit_cost_mad))
        phase_infra_cost = _q(_to_dec(actual_vehicles) * _to_dec(irve_cost_per_vehicle_mad))
        phase_total_cost = _q(phase_vehicle_cost + phase_infra_cost)

        budget_remaining -= phase_total_cost
        total_cost += phase_total_cost
        total_vehicles_converted += actual_vehicles

        cumulative_pct = _q(
            _to_dec(total_vehicles_converted) / _to_dec(fleet_size) * Decimal("100")
        )

        phases.append({
            "name": wave_key,
            "technology_wave": wave_key,
            "description": wave["description"],
            "start_year": phase_start,
            "end_year": phase_end,
            "duration_years": duration,
            "vehicles_to_convert": actual_vehicles,
            "target_pct_electric": float(cumulative_pct),
            "budget_allocated_mad": float(phase_total_cost),
            "vehicle_cost_mad": float(phase_vehicle_cost),
            "infrastructure_cost_mad": float(phase_infra_cost),
            "status": "planned",
        })

        phase_start = phase_end

    # ---- Milestones -------------------------------------------------------
    milestones = compute_phase_milestones(phases, fleet_size)

    # ---- Budget surplus / deficit -----------------------------------------
    surplus_or_deficit = _q(_to_dec(total_budget_mad) - total_cost)

    logger.info(
        "Transition plan generated: scenario=%s, fleet=%d, "
        "vehicles_converted=%d/%d, cost=%s/%s %s, surplus=%s %s",
        scenario_type,
        fleet_size,
        total_vehicles_converted,
        fleet_size,
        float(_q(total_cost)),
        total_budget_mad,
        currency,
        float(surplus_or_deficit),
        currency,
    )

    return {
        "plan_name": f"Plan electrification {scenario_type} ({start_year})",
        "scenario_type": scenario_type,
        "fleet_size": fleet_size,
        "total_budget_mad": total_budget_mad,
        "phases": phases,
        "total_phases": len(phases),
        "total_vehicles_converted": total_vehicles_converted,
        "total_cost_mad": float(_q(total_cost)),
        "budget_surplus_or_deficit_mad": float(surplus_or_deficit),
        "milestones": milestones,
        "currency": currency,
    }
