from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

from app.db.seed_vehicles import VEHICLE_REFERENCE_DATA

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default cost parameters per motorization (used when no overrides provided)
# These are per-vehicle annual defaults derived from PRD benchmarks.
# ---------------------------------------------------------------------------

DEFAULT_COSTS: dict[str, dict[str, Decimal]] = {
    "diesel": {
        "purchase_price": Decimal("180000"),
        "annual_maintenance_cost": Decimal("12000"),
        "energy_cost_per_km": Decimal("0.15"),
        "annual_km": Decimal("40000"),
        "residual_value": Decimal("30000"),
    },
    "hybrid": {
        "purchase_price": Decimal("220000"),
        "annual_maintenance_cost": Decimal("10000"),
        "energy_cost_per_km": Decimal("0.12"),
        "annual_km": Decimal("40000"),
        "residual_value": Decimal("35000"),
    },
    "electric": {
        "purchase_price": Decimal("300000"),
        "annual_maintenance_cost": Decimal("6000"),
        "energy_cost_per_km": Decimal("0.06"),
        "annual_km": Decimal("40000"),
        "residual_value": Decimal("50000"),
    },
    "hydrogen": {
        "purchase_price": Decimal("400000"),
        "annual_maintenance_cost": Decimal("8000"),
        "energy_cost_per_km": Decimal("0.20"),
        "annual_km": Decimal("40000"),
        "residual_value": Decimal("40000"),
    },
    "gnv": {
        "purchase_price": Decimal("200000"),
        "annual_maintenance_cost": Decimal("11000"),
        "energy_cost_per_km": Decimal("0.10"),
        "annual_km": Decimal("40000"),
        "residual_value": Decimal("28000"),
    },
}

# Map vehicle type to a purchase price multiplier relative to the midibus baseline
VEHICLE_TYPE_MULTIPLIERS: dict[str, Decimal] = {
    "vehicule_leger": Decimal("0.45"),
    "minibus": Decimal("0.72"),
    "midibus": Decimal("1.00"),
    "bus_standard": Decimal("1.40"),
    "grand_bus": Decimal("2.00"),
}


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_defaults(
    vehicle_type: str,
    motorization: str,
) -> dict[str, Decimal]:
    """Return default cost params for a vehicle type + motorization combo."""
    base = DEFAULT_COSTS.get(motorization, DEFAULT_COSTS["diesel"]).copy()
    mult = VEHICLE_TYPE_MULTIPLIERS.get(vehicle_type, Decimal("1.00"))
    base["purchase_price"] = _q(base["purchase_price"] * mult)
    base["annual_maintenance_cost"] = _q(base["annual_maintenance_cost"] * mult)
    base["residual_value"] = _q(base["residual_value"] * mult)
    return base


# ---------------------------------------------------------------------------
# Core TCO formula
# ---------------------------------------------------------------------------


def compute_tco_single(
    purchase_price: Decimal,
    annual_maintenance_cost: Decimal,
    energy_cost_per_km: Decimal,
    annual_km: Decimal,
    residual_value: Decimal,
    duration_years: int,
    quantity: int = 1,
) -> dict:
    """
    Compute TCO for a single vehicle specification.

    TCO = Purchase + (Maintenance × Duration) + (Energy_per_km × Annual_km × Duration) − Residual

    Returns dict with tco_per_vehicle, tco_total (× quantity), and component breakdown.
    """
    maintenance_total = _q(annual_maintenance_cost * duration_years)
    energy_total = _q(energy_cost_per_km * annual_km * duration_years)
    tco_per_vehicle = _q(purchase_price + maintenance_total + energy_total - residual_value)
    tco_total = _q(tco_per_vehicle * quantity)

    return {
        "purchase_price": float(purchase_price),
        "annual_maintenance_cost": float(annual_maintenance_cost),
        "energy_cost_per_km": float(energy_cost_per_km),
        "annual_km": float(annual_km),
        "residual_value": float(residual_value),
        "duration_years": duration_years,
        "quantity": quantity,
        "maintenance_total": float(maintenance_total),
        "energy_total": float(energy_total),
        "tco_per_vehicle": float(tco_per_vehicle),
        "tco_total": float(tco_total),
    }


# ---------------------------------------------------------------------------
# Year-by-year evolution
# ---------------------------------------------------------------------------


def compute_tco_evolution(
    purchase_price: Decimal,
    annual_maintenance_cost: Decimal,
    energy_cost_per_km: Decimal,
    annual_km: Decimal,
    residual_value: Decimal,
    max_years: int = 10,
    quantity: int = 1,
) -> list[dict]:
    """
    Return year-by-year cumulative TCO for years 1..max_years.

    Residual value is only deducted at the final year of each calculation,
    making the series monotonically increasing in practice.
    """
    evolution: list[dict] = []
    for year in range(1, max_years + 1):
        result = compute_tco_single(
            purchase_price=purchase_price,
            annual_maintenance_cost=annual_maintenance_cost,
            energy_cost_per_km=energy_cost_per_km,
            annual_km=annual_km,
            residual_value=residual_value,
            duration_years=year,
            quantity=quantity,
        )
        evolution.append({
            "year": year,
            "tco_per_vehicle": result["tco_per_vehicle"],
            "tco_total": result["tco_total"],
        })
    return evolution


# ---------------------------------------------------------------------------
# Motorization comparison
# ---------------------------------------------------------------------------


def compare_motorizations(
    vehicle_type: str,
    duration_years: int = 5,
    quantity: int = 1,
    overrides: dict[str, dict[str, float]] | None = None,
) -> list[dict]:
    """
    Compute TCO for all available motorizations for a given vehicle type.

    overrides: optional dict keyed by motorization with cost override values.
    Returns list sorted by tco_per_vehicle ascending (cheapest first).
    """
    # Look up available motorizations for this vehicle type
    ref = next(
        (r for r in VEHICLE_REFERENCE_DATA if r["type"] == vehicle_type),
        None,
    )
    motorizations = (
        ref["motorizations_available"]
        if ref is not None
        else list(DEFAULT_COSTS.keys())
    )

    results: list[dict] = []
    for motor in motorizations:
        defaults = _get_defaults(vehicle_type, motor)

        # Apply overrides if provided for this motorization
        if overrides and motor in overrides:
            for key, val in overrides[motor].items():
                if key in defaults:
                    defaults[key] = Decimal(str(val))

        tco = compute_tco_single(
            purchase_price=defaults["purchase_price"],
            annual_maintenance_cost=defaults["annual_maintenance_cost"],
            energy_cost_per_km=defaults["energy_cost_per_km"],
            annual_km=defaults["annual_km"],
            residual_value=defaults["residual_value"],
            duration_years=duration_years,
            quantity=quantity,
        )
        results.append({
            "motorization": motor,
            **tco,
        })

    results.sort(key=lambda r: r["tco_per_vehicle"])
    return results


# ---------------------------------------------------------------------------
# Fleet-level TCO
# ---------------------------------------------------------------------------


def compute_fleet_tco(
    fleet: list[dict],
    duration_years: int = 5,
) -> dict:
    """
    Compute aggregate TCO for a fleet composition.

    fleet: list of dicts, each with:
        - vehicle_type: str
        - motorization: str
        - quantity: int (default 1)
        - optional cost overrides (purchase_price, annual_maintenance_cost, etc.)

    Returns per-vehicle breakdowns + fleet totals.
    """
    vehicles: list[dict] = []
    fleet_total = Decimal("0")

    for spec in fleet:
        vehicle_type = spec["vehicle_type"]
        motorization = spec.get("motorization", "diesel")
        quantity = spec.get("quantity", 1)

        defaults = _get_defaults(vehicle_type, motorization)

        # Apply any inline overrides
        for key in [
            "purchase_price",
            "annual_maintenance_cost",
            "energy_cost_per_km",
            "annual_km",
            "residual_value",
        ]:
            if key in spec and spec[key] is not None:
                defaults[key] = Decimal(str(spec[key]))

        tco = compute_tco_single(
            purchase_price=defaults["purchase_price"],
            annual_maintenance_cost=defaults["annual_maintenance_cost"],
            energy_cost_per_km=defaults["energy_cost_per_km"],
            annual_km=defaults["annual_km"],
            residual_value=defaults["residual_value"],
            duration_years=duration_years,
            quantity=quantity,
        )

        fleet_total += Decimal(str(tco["tco_total"]))
        vehicles.append({
            "vehicle_type": vehicle_type,
            "motorization": motorization,
            **tco,
        })

    return {
        "duration_years": duration_years,
        "vehicles": vehicles,
        "fleet_tco_total": float(_q(fleet_total)),
        "vehicle_count": sum(v["quantity"] for v in vehicles),
    }


# ---------------------------------------------------------------------------
# Full TCO calculation (combines all above)
# ---------------------------------------------------------------------------


def calculate_tco(
    fleet: list[dict],
    duration_years: int = 5,
    include_evolution: bool = True,
    include_comparison: bool = True,
) -> dict:
    """
    Main entry point: compute fleet TCO with optional evolution and comparison.

    Returns:
        - fleet_tco: aggregate fleet TCO breakdown
        - evolution: year-by-year for the entire fleet (if requested)
        - motorization_comparisons: per vehicle_type comparison (if requested)
    """
    fleet_result = compute_fleet_tco(fleet, duration_years)

    result: dict = {"fleet_tco": fleet_result}

    # Evolution: sum fleet TCO for each year
    if include_evolution:
        max_years = min(duration_years, 10)
        yearly: list[dict] = []
        for year in range(1, max_years + 1):
            year_fleet = compute_fleet_tco(fleet, year)
            yearly.append({
                "year": year,
                "fleet_tco_total": year_fleet["fleet_tco_total"],
            })
        result["evolution"] = yearly

    # Motorization comparison for each unique vehicle type in fleet
    if include_comparison:
        seen_types: set[str] = set()
        comparisons: list[dict] = []
        for spec in fleet:
            vtype = spec["vehicle_type"]
            if vtype not in seen_types:
                seen_types.add(vtype)
                quantity = spec.get("quantity", 1)
                comp = compare_motorizations(
                    vehicle_type=vtype,
                    duration_years=duration_years,
                    quantity=quantity,
                )
                comparisons.append({
                    "vehicle_type": vtype,
                    "motorizations": comp,
                })
        result["motorization_comparisons"] = comparisons

    return result
