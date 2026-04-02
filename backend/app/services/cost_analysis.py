from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# French standard
DEFAULT_WORKING_DAYS = 220
TRIPS_PER_DAY = 2


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_cost_per_available_seat(
    annual_route_cost: Decimal,
    vehicle_capacity: int,
    working_days: int = DEFAULT_WORKING_DAYS,
    trips_per_day: int = TRIPS_PER_DAY,
) -> Decimal:
    """
    Cost per available seat = Annual route cost / (capacity × working days × trips/day).
    """
    total_seat_trips = Decimal(str(vehicle_capacity * working_days * trips_per_day))
    if total_seat_trips == 0:
        return Decimal("0")
    return _q(annual_route_cost / total_seat_trips)


def compute_cost_per_occupied_seat(
    cost_per_available_seat: Decimal,
    fill_rate: Decimal,
) -> Decimal:
    """
    Cost per occupied seat = cost per available seat / fill rate.
    """
    if fill_rate <= 0:
        return Decimal("0")
    return _q(cost_per_available_seat / fill_rate)


def compute_annual_cost_per_employee(
    total_annual_cost: Decimal,
    transported_employees: int,
) -> Decimal:
    """
    Annual cost per transported employee = total annual cost / number of employees.
    """
    if transported_employees <= 0:
        return Decimal("0")
    return _q(total_annual_cost / transported_employees)


def compute_breakeven_point(
    annual_transport_cost: Decimal,
    average_distance_km: Decimal,
    kilometric_allowance_per_km: Decimal,
    working_days: int = DEFAULT_WORKING_DAYS,
    trips_per_day: int = TRIPS_PER_DAY,
) -> int:
    """
    Breakeven: minimum N employees where transport < kilometric allowance.

    N_breakeven = Annual_Transport_Cost / Annual_Kilometric_Allowance_per_Employee
    Where: annual_allowance_per_employee = avg_distance × cost/km × working_days × trips/day
    """
    annual_allowance_per_employee = _q(
        average_distance_km * kilometric_allowance_per_km
        * working_days * trips_per_day
    )
    if annual_allowance_per_employee <= 0:
        return 0
    # Ceiling: need at least this many employees for transport to break even
    raw = annual_transport_cost / annual_allowance_per_employee
    import math
    return math.ceil(float(raw))


def generate_breakeven_curves(
    annual_transport_cost: Decimal,
    average_distance_km: Decimal,
    kilometric_allowance_per_km: Decimal,
    working_days: int = DEFAULT_WORKING_DAYS,
    trips_per_day: int = TRIPS_PER_DAY,
    max_employees: int = 100,
) -> list[dict]:
    """
    Generate data points for breakeven chart.

    Returns list of {employees, transport_cost_per_employee, allowance_cost_per_employee}.
    """
    annual_allowance_per_employee = float(_q(
        average_distance_km * kilometric_allowance_per_km
        * working_days * trips_per_day
    ))
    annual_transport = float(annual_transport_cost)

    points: list[dict] = []
    for n in range(1, max_employees + 1):
        transport_per_emp = round(annual_transport / n, 2)
        allowance_per_emp = round(annual_allowance_per_employee, 2)
        points.append({
            "employees": n,
            "transport_cost_per_employee": transport_per_emp,
            "allowance_cost_per_employee": allowance_per_emp,
        })
    return points


def calculate_cost_analysis(
    annual_route_cost: Decimal,
    vehicle_capacity: int,
    fill_rate: Decimal,
    transported_employees: int,
    average_distance_km: Decimal,
    kilometric_allowance_per_km: Decimal,
    working_days: int = DEFAULT_WORKING_DAYS,
    trips_per_day: int = TRIPS_PER_DAY,
    total_annual_cost: Decimal | None = None,
) -> dict:
    """
    Full cost analysis: per-seat costs, per-employee cost, breakeven, and chart data.
    """
    effective_total = total_annual_cost if total_annual_cost is not None else annual_route_cost

    cost_per_available = compute_cost_per_available_seat(
        annual_route_cost, vehicle_capacity, working_days, trips_per_day,
    )
    cost_per_occupied = compute_cost_per_occupied_seat(cost_per_available, fill_rate)
    cost_per_employee = compute_annual_cost_per_employee(effective_total, transported_employees)
    breakeven = compute_breakeven_point(
        effective_total, average_distance_km, kilometric_allowance_per_km,
        working_days, trips_per_day,
    )

    # Annual kilometric allowance per employee
    annual_allowance_per_employee = float(_q(
        average_distance_km * kilometric_allowance_per_km
        * working_days * trips_per_day
    ))

    # Breakeven chart data (up to 2× breakeven or min 50)
    max_chart = max(breakeven * 2, 50) if breakeven > 0 else 50
    chart_data = generate_breakeven_curves(
        effective_total, average_distance_km, kilometric_allowance_per_km,
        working_days, trips_per_day, max_employees=min(max_chart, 200),
    )

    return {
        "cost_per_available_seat": float(cost_per_available),
        "cost_per_occupied_seat": float(cost_per_occupied),
        "annual_cost_per_employee": float(cost_per_employee),
        "breakeven_employees": breakeven,
        "annual_route_cost": float(annual_route_cost),
        "vehicle_capacity": vehicle_capacity,
        "fill_rate": float(fill_rate),
        "transported_employees": transported_employees,
        "working_days": working_days,
        "trips_per_day": trips_per_day,
        "annual_allowance_per_employee": annual_allowance_per_employee,
        "breakeven_chart": chart_data,
    }
