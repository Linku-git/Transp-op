from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ligne import Ligne


def compute_line_km_annual(
    distance_km: float, rotations: int, operating_days: int
) -> float:
    """CDC formula: km_annual = D x R x J."""
    return distance_km * rotations * operating_days


async def compute_fleet_diagnostics(
    db: AsyncSession, tenant_id: uuid.UUID
) -> dict:
    """Aggregate all active lignes into a fleet context snapshot."""
    base = [Ligne.tenant_id == tenant_id, Ligne.is_active.is_(True)]

    # Total count and km aggregation
    agg_stmt = select(
        func.count(Ligne.id).label("total_vehicles"),
        func.coalesce(func.sum(Ligne.km_annual), 0.0).label("total_km_annual"),
    ).where(*base)
    agg_result = await db.execute(agg_stmt)
    agg_row = agg_result.one()

    total_vehicles = agg_row.total_vehicles
    total_km_annual = float(agg_row.total_km_annual)

    if total_vehicles == 0:
        return {
            "total_vehicles": 0,
            "total_km_annual": 0.0,
            "total_tco2_annual": 0.0,
            "average_age_years": None,
            "pct_diesel": 0.0,
            "pct_electric": 0.0,
            "pct_hybrid": 0.0,
            "currency": "MAD",
            "snapshot_date": date.today(),
        }

    # Motorization breakdown
    motor_stmt = (
        select(
            Ligne.motorization,
            func.count(Ligne.id).label("cnt"),
        )
        .where(*base)
        .group_by(Ligne.motorization)
    )
    motor_result = await db.execute(motor_stmt)
    motor_rows = motor_result.all()

    motor_counts: dict[str | None, int] = {}
    for row in motor_rows:
        motor_counts[row.motorization] = row.cnt

    pct_diesel = motor_counts.get("diesel", 0) / total_vehicles * 100
    pct_electric = motor_counts.get("electric", 0) / total_vehicles * 100
    pct_hybrid = motor_counts.get("hybrid", 0) / total_vehicles * 100

    # Estimate CO2: diesel ~2.6 kg/km, hybrid ~1.5 kg/km, electric ~0 kg/km
    co2_factors = {"diesel": 2.6, "hybrid": 1.5, "electric": 0.0}
    total_tco2 = 0.0
    for motor, cnt in motor_counts.items():
        factor = co2_factors.get(motor or "", 2.6)  # default to diesel factor
        # Approximate per-line km
        if total_vehicles > 0:
            avg_km = total_km_annual / total_vehicles
            total_tco2 += avg_km * cnt * factor / 1000  # tonnes

    return {
        "total_vehicles": total_vehicles,
        "total_km_annual": round(total_km_annual, 2),
        "total_tco2_annual": round(total_tco2, 2),
        "average_age_years": None,
        "pct_diesel": round(pct_diesel, 2),
        "pct_electric": round(pct_electric, 2),
        "pct_hybrid": round(pct_hybrid, 2),
        "currency": "MAD",
        "snapshot_date": date.today(),
    }
