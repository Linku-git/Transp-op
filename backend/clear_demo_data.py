"""
Clear all demo/seed data while preserving:
- Tenant, Roles, Users (auth core)
- System permissions
Each table uses its own savepoint so one failure doesn't abort others.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:password@helium:5432/heliumdb"

TABLES = [
    "route",
    "cluster",
    "optimization",
    "roi_calculation",
    "tco_entry",
    "financial_scenario",
    "generated_report",
    "kpi_snapshot",
    "employee_leave",
    "weather_forecast",
    "employee_modal",
    "employee",
    "vehicle",
    "point_arret",
    "horaire_travail",
    "config_transport_vehicle",
    "km_consommation",
    "scenario",
    "site",
]


async def clear():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        async with db.begin():
            for t in TABLES:
                sp = f"sp_{t}"
                await db.execute(text(f"SAVEPOINT {sp}"))
                try:
                    result = await db.execute(text(f"DELETE FROM {t}"))
                    print(f"  Deleted {result.rowcount:>4} rows from {t}")
                    await db.execute(text(f"RELEASE SAVEPOINT {sp}"))
                except Exception as e:
                    await db.execute(text(f"ROLLBACK TO SAVEPOINT {sp}"))
                    short = str(e).split("\n")[0]
                    print(f"  Skipped {t}: {short}")

    await engine.dispose()
    print("\nDone — auth data preserved (tenant, roles, users).")


if __name__ == "__main__":
    asyncio.run(clear())
