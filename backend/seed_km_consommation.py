"""
Seed script — Type Véhicules & Consommation Gasoil (exact data from source)
Run from backend/ directory:  python seed_km_consommation.py
"""
import asyncio
import asyncpg
from decimal import Decimal

DB_URL = "postgresql://postgres:password@helium:5432/heliumdb"

# fmt: off
# (prestataire, vehicle_type, vehicle_count_peak,
#  km_avg, km_min, km_max, seat_count,
#  fuel_consumption_l100km, monthly_cost_per_vehicle_mad)
ROWS = [
    # ── STCR ──────────────────────────────────────────────────────────────────
    ("STCR",       "Autocars",    13,  8948.00,  7313.00,  8854.00, 48, 34.00, 114721.20),
    ("STCR",       "Minibus 17",   9,  2811.00,  1981.00,  4192.00, 17, 13.00,  23760.00),
    ("STCR",       "Minibus 20",   5,  6360.00,  4653.00,  8502.00, 20, 11.00,  44550.00),
    ("STCR",       "Minicar 30",   3,  7141.00,  6531.00,  7479.00, 30, 21.00,  59400.00),
    # ── S/TOURISME ────────────────────────────────────────────────────────────
    ("S/TOURISME",  "Autocars",   12,  8632.00,  7240.00, 10146.00, 48, 34.00, 113330.80),
    ("S/TOURISME",  "Minicar 30",  5,  7094.00,  5352.00,  9570.00, 30, 21.00,  59400.00),
    # ── MANAVETTE ─────────────────────────────────────────────────────────────
    ("MANAVETTE",  "Minibus 17",   8,  3722.00,  1489.00,  5090.00, 17, 13.00,  23760.00),
    # ── CTM ───────────────────────────────────────────────────────────────────
    ("CTM",        "Autocars",     4, 10600.00,  9500.00, 11600.00, 48, 35.00, 121990.00),
    # ── SOTREG ────────────────────────────────────────────────────────────────
    ("SOTREG",     "Autocars",    32,  5500.00,     None,  7500.00, 48, 41.00,  38250.00),
    ("SOTREG",     "Minibus 17",   4,  1500.00,  1000.00,  3000.00, 17, 17.00,  22750.00),
]
# fmt: on

assert len(ROWS) == 10, f"Expected 10 rows, got {len(ROWS)}"


async def seed():
    conn = await asyncpg.connect(DB_URL)
    tenant_id = await conn.fetchval("SELECT id FROM tenant LIMIT 1")
    print(f"Tenant: {tenant_id}")

    deleted = await conn.execute(
        "DELETE FROM km_consommation WHERE tenant_id = $1", tenant_id
    )
    print(f"Cleared: {deleted}")

    for (prestataire, vehicle_type, count,
         km_avg, km_min, km_max, seats, fuel, cost) in ROWS:

        await conn.execute(
            """
            INSERT INTO km_consommation (
                id, tenant_id,
                prestataire, vehicle_type, vehicle_count_peak,
                km_avg, km_min, km_max,
                seat_count, fuel_consumption_l100km,
                monthly_cost_per_vehicle_mad
            ) VALUES (
                gen_random_uuid(), $1,
                $2, $3, $4,
                $5, $6, $7,
                $8, $9,
                $10
            )
            """,
            tenant_id,
            prestataire, vehicle_type, count,
            Decimal(str(km_avg)) if km_avg is not None else None,
            Decimal(str(km_min)) if km_min is not None else None,
            Decimal(str(km_max)) if km_max is not None else None,
            seats,
            Decimal(str(fuel)),
            Decimal(str(cost)),
        )

    await conn.close()

    print(f"\nInserted: {len(ROWS)} rows")
    for row in ROWS:
        print(f"  {row[0]:<12} | {row[1]:<12} | {row[2]:>3} véh. | "
              f"avg={row[3]:>8.0f} km | fuel={row[7]}% | coût={row[8]:>11,.2f} MAD")


if __name__ == "__main__":
    asyncio.run(seed())
