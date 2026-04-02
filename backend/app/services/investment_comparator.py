from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Individual investment models
# ---------------------------------------------------------------------------


def compute_capex(
    vehicle_count: int,
    purchase_price_per_vehicle: Decimal,
    annual_maintenance_per_vehicle: Decimal,
    annual_fuel_per_vehicle: Decimal,
    annual_insurance_per_vehicle: Decimal,
    annual_driver_cost_per_vehicle: Decimal,
    residual_value_per_vehicle: Decimal,
    duration_years: int,
    headcount: int,
    annual_trips: int,
) -> dict:
    """
    CAPEX model: own fleet.

    Total = (Purchase × Vehicles) + (Maintenance + Fuel + Insurance + Driver) × Vehicles × Years − Residual × Vehicles
    """
    total_purchase = _q(purchase_price_per_vehicle * vehicle_count)
    annual_ops = _q(
        (annual_maintenance_per_vehicle + annual_fuel_per_vehicle
         + annual_insurance_per_vehicle + annual_driver_cost_per_vehicle)
        * vehicle_count
    )
    total_ops = _q(annual_ops * duration_years)
    total_residual = _q(residual_value_per_vehicle * vehicle_count)
    total_cost = _q(total_purchase + total_ops - total_residual)
    annual_cost = _q(total_cost / duration_years) if duration_years > 0 else Decimal("0")
    cost_per_employee = _q(total_cost / headcount) if headcount > 0 else Decimal("0")
    cost_per_trip = _q(total_cost / (annual_trips * duration_years)) if annual_trips > 0 and duration_years > 0 else Decimal("0")

    return {
        "model": "capex",
        "label": "CAPEX (Own Fleet)",
        "total_cost": float(total_cost),
        "annual_cost": float(annual_cost),
        "cost_per_employee": float(cost_per_employee),
        "cost_per_trip": float(cost_per_trip),
        "duration_years": duration_years,
        "vehicle_count": vehicle_count,
        "breakdown": {
            "total_purchase": float(total_purchase),
            "total_operations": float(total_ops),
            "total_residual": float(total_residual),
            "annual_operations": float(annual_ops),
        },
    }


def compute_mise_a_disposition(
    vehicle_count: int,
    monthly_rental_per_vehicle: Decimal,
    annual_fuel_per_vehicle: Decimal,
    management_overhead_rate: Decimal,
    duration_years: int,
    headcount: int,
    annual_trips: int,
) -> dict:
    """
    Mise a disposition model: vehicle rental with operational costs.

    Total = (Monthly_Rental × 12 × Vehicles × Years) + (Fuel × Vehicles × Years) + Management_Overhead
    """
    annual_rental = _q(monthly_rental_per_vehicle * 12 * vehicle_count)
    total_rental = _q(annual_rental * duration_years)
    total_fuel = _q(annual_fuel_per_vehicle * vehicle_count * duration_years)
    subtotal = _q(total_rental + total_fuel)
    management_overhead = _q(subtotal * management_overhead_rate)
    total_cost = _q(subtotal + management_overhead)
    annual_cost = _q(total_cost / duration_years) if duration_years > 0 else Decimal("0")
    cost_per_employee = _q(total_cost / headcount) if headcount > 0 else Decimal("0")
    cost_per_trip = _q(total_cost / (annual_trips * duration_years)) if annual_trips > 0 and duration_years > 0 else Decimal("0")

    return {
        "model": "mise_a_disposition",
        "label": "Mise à Disposition",
        "total_cost": float(total_cost),
        "annual_cost": float(annual_cost),
        "cost_per_employee": float(cost_per_employee),
        "cost_per_trip": float(cost_per_trip),
        "duration_years": duration_years,
        "vehicle_count": vehicle_count,
        "breakdown": {
            "total_rental": float(total_rental),
            "total_fuel": float(total_fuel),
            "management_overhead": float(management_overhead),
            "annual_rental": float(annual_rental),
        },
    }


def compute_opex(
    cost_per_km: Decimal,
    annual_km_per_vehicle: Decimal,
    vehicle_count: int,
    duration_years: int,
    headcount: int,
    annual_trips: int,
) -> dict:
    """
    OPEX model: full outsource to transport operator.

    Total = Cost_per_km × Annual_km × Vehicles × Years
    No capital investment.
    """
    annual_cost_total = _q(cost_per_km * annual_km_per_vehicle * vehicle_count)
    total_cost = _q(annual_cost_total * duration_years)
    cost_per_employee = _q(total_cost / headcount) if headcount > 0 else Decimal("0")
    cost_per_trip = _q(total_cost / (annual_trips * duration_years)) if annual_trips > 0 and duration_years > 0 else Decimal("0")

    return {
        "model": "opex",
        "label": "OPEX (Full Outsource)",
        "total_cost": float(total_cost),
        "annual_cost": float(annual_cost_total),
        "cost_per_employee": float(cost_per_employee),
        "cost_per_trip": float(cost_per_trip),
        "duration_years": duration_years,
        "vehicle_count": vehicle_count,
        "breakdown": {
            "annual_km_total": float(_q(annual_km_per_vehicle * vehicle_count)),
            "cost_per_km": float(cost_per_km),
        },
    }


# ---------------------------------------------------------------------------
# Recommendation logic
# ---------------------------------------------------------------------------


def recommend_model(models: list[dict], vehicle_count: int, duration_years: int) -> dict:
    """
    Recommend the optimal investment model.

    Heuristic:
    - Small fleet (≤5 vehicles) or short duration (≤2 years): prefer OPEX
    - Medium fleet (6-15): prefer Mise a disposition
    - Large fleet (>15) and long duration (>3 years): prefer CAPEX
    - Override with lowest total cost if the heuristic pick is >20% more expensive.
    """
    sorted_by_cost = sorted(models, key=lambda m: m["total_cost"])
    cheapest = sorted_by_cost[0]

    if vehicle_count <= 5 or duration_years <= 2:
        heuristic_pick = "opex"
    elif vehicle_count <= 15:
        heuristic_pick = "mise_a_disposition"
    else:
        heuristic_pick = "capex"

    heuristic_model = next((m for m in models if m["model"] == heuristic_pick), cheapest)

    # Override if heuristic is >20% more expensive than cheapest
    if heuristic_model["total_cost"] > cheapest["total_cost"] * 1.20:
        recommended = cheapest
        reason = f"Lowest total cost ({cheapest['model']}), heuristic pick ({heuristic_pick}) was >20% more expensive"
    else:
        recommended = heuristic_model
        reason_map = {
            "opex": f"Recommended for small fleet ({vehicle_count} vehicles) or short duration ({duration_years}y) — minimal capital commitment",
            "mise_a_disposition": f"Recommended for medium fleet ({vehicle_count} vehicles) — balanced flexibility and cost",
            "capex": f"Recommended for large fleet ({vehicle_count} vehicles) over {duration_years} years — lowest long-term cost of ownership",
        }
        reason = reason_map.get(heuristic_pick, "Lowest total cost")

    return {
        "recommended_model": recommended["model"],
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# Side-by-side comparison
# ---------------------------------------------------------------------------


def compare_investment_models(
    vehicle_count: int,
    headcount: int,
    annual_trips: int,
    duration_years: int,
    # CAPEX params
    capex_purchase_price: Decimal,
    capex_annual_maintenance: Decimal,
    capex_annual_fuel: Decimal,
    capex_annual_insurance: Decimal,
    capex_annual_driver_cost: Decimal,
    capex_residual_value: Decimal,
    # MaD params
    mad_monthly_rental: Decimal,
    mad_annual_fuel: Decimal,
    mad_management_overhead_rate: Decimal,
    # OPEX params
    opex_cost_per_km: Decimal,
    opex_annual_km: Decimal,
) -> dict:
    """Compute all 3 models and return side-by-side comparison with recommendation."""
    capex = compute_capex(
        vehicle_count=vehicle_count,
        purchase_price_per_vehicle=capex_purchase_price,
        annual_maintenance_per_vehicle=capex_annual_maintenance,
        annual_fuel_per_vehicle=capex_annual_fuel,
        annual_insurance_per_vehicle=capex_annual_insurance,
        annual_driver_cost_per_vehicle=capex_annual_driver_cost,
        residual_value_per_vehicle=capex_residual_value,
        duration_years=duration_years,
        headcount=headcount,
        annual_trips=annual_trips,
    )

    mad = compute_mise_a_disposition(
        vehicle_count=vehicle_count,
        monthly_rental_per_vehicle=mad_monthly_rental,
        annual_fuel_per_vehicle=mad_annual_fuel,
        management_overhead_rate=mad_management_overhead_rate,
        duration_years=duration_years,
        headcount=headcount,
        annual_trips=annual_trips,
    )

    opex = compute_opex(
        cost_per_km=opex_cost_per_km,
        annual_km_per_vehicle=opex_annual_km,
        vehicle_count=vehicle_count,
        duration_years=duration_years,
        headcount=headcount,
        annual_trips=annual_trips,
    )

    models = [capex, mad, opex]
    recommendation = recommend_model(models, vehicle_count, duration_years)

    return {
        "models": models,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------------


def sensitivity_analysis(
    baseline_params: dict,
    fuel_price_delta_pct: float = 0.0,
    headcount_delta_pct: float = 0.0,
    fill_rate_pct: float = 100.0,
) -> dict:
    """
    Recompute all 3 models with adjusted parameters and return deltas vs baseline.

    - fuel_price_delta_pct: e.g. +30 means fuel costs increase 30%
    - headcount_delta_pct: e.g. -50 means 50% fewer employees
    - fill_rate_pct: 50-100, affects cost per employee/trip (fewer people, same fleet)
    """
    # Deep copy and adjust params
    params = {k: v for k, v in baseline_params.items()}

    # Adjust fuel
    fuel_mult = Decimal(str(1 + fuel_price_delta_pct / 100))
    params["capex_annual_fuel"] = _q(Decimal(str(params["capex_annual_fuel"])) * fuel_mult)
    params["mad_annual_fuel"] = _q(Decimal(str(params["mad_annual_fuel"])) * fuel_mult)

    # Adjust headcount
    hc_mult = 1 + headcount_delta_pct / 100
    params["headcount"] = max(1, int(params["headcount"] * hc_mult))

    # Adjust effective headcount for fill rate
    effective_fill = max(0.5, fill_rate_pct / 100)
    params["headcount"] = max(1, int(params["headcount"] * effective_fill))
    params["annual_trips"] = max(1, int(params["annual_trips"] * effective_fill))

    # Convert all Decimal-like params
    decimal_keys = [
        "capex_purchase_price", "capex_annual_maintenance", "capex_annual_fuel",
        "capex_annual_insurance", "capex_annual_driver_cost", "capex_residual_value",
        "mad_monthly_rental", "mad_annual_fuel", "mad_management_overhead_rate",
        "opex_cost_per_km", "opex_annual_km",
    ]
    for key in decimal_keys:
        if key in params:
            params[key] = Decimal(str(params[key]))

    adjusted = compare_investment_models(**params)

    # Compute baseline
    baseline_decimal = {k: v for k, v in baseline_params.items()}
    for key in decimal_keys:
        if key in baseline_decimal:
            baseline_decimal[key] = Decimal(str(baseline_decimal[key]))
    baseline = compare_investment_models(**baseline_decimal)

    # Compute deltas
    deltas: list[dict] = []
    for adj_model, base_model in zip(adjusted["models"], baseline["models"]):
        deltas.append({
            "model": adj_model["model"],
            "total_cost_delta": round(adj_model["total_cost"] - base_model["total_cost"], 2),
            "annual_cost_delta": round(adj_model["annual_cost"] - base_model["annual_cost"], 2),
            "cost_per_employee_delta": round(adj_model["cost_per_employee"] - base_model["cost_per_employee"], 2),
        })

    return {
        "adjusted_params": {
            "fuel_price_delta_pct": fuel_price_delta_pct,
            "headcount_delta_pct": headcount_delta_pct,
            "fill_rate_pct": fill_rate_pct,
        },
        "baseline": baseline,
        "adjusted": adjusted,
        "deltas": deltas,
    }
