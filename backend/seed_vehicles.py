"""
Seed script — Parc Véhicule SOTREG (106 vehicles, exact from source)
Run from backend/ directory:  python seed_vehicles.py
"""
import asyncio
import asyncpg
from datetime import date

DB_URL = "postgresql://postgres:password@helium:5432/heliumdb"


def d(s: str) -> date:
    m, day, y = s.split("/")
    return date(int(y), int(m), int(day))


# fmt: off
VEHICLES = [
    # matricule, type, brand_model, capacity, circ_date, owner/prestataire
    # ── SOTREG — Autocars CAR-MAN ────────────────────────────────────────────
    ("22363",  "Autocar", "MAN", 54, "5/30/2011",  "SOTREG"),
    ("22401",  "Autocar", "MAN", 54, "1/18/2012",  "SOTREG"),
    ("22405",  "Autocar", "MAN", 54, "1/18/2012",  "SOTREG"),
    ("22410",  "Autocar", "MAN", 54, "1/19/2012",  "SOTREG"),
    ("22420",  "Autocar", "MAN", 54, "2/17/2012",  "SOTREG"),
    ("22421",  "Autocar", "MAN", 42, "2/17/2012",  "SOTREG"),
    ("22422",  "Autocar", "MAN", 54, "2/17/2012",  "SOTREG"),
    ("22423",  "Autocar", "MAN", 54, "2/17/2012",  "SOTREG"),
    ("22424",  "Autocar", "MAN", 48, "2/17/2012",  "SOTREG"),
    ("22425",  "Autocar", "MAN", 54, "3/22/2012",  "SOTREG"),
    ("22426",  "Autocar", "MAN", 54, "3/22/2012",  "SOTREG"),
    ("22427",  "Autocar", "MAN", 54, "3/22/2012",  "SOTREG"),
    ("22429",  "Autocar", "MAN", 42, "3/22/2012",  "SOTREG"),
    ("22430",  "Autocar", "MAN", 40, "3/22/2012",  "SOTREG"),
    ("22431",  "Autocar", "MAN", 42, "5/15/2012",  "SOTREG"),
    ("22433",  "Autocar", "MAN", 42, "5/15/2012",  "SOTREG"),
    ("22434",  "Autocar", "MAN", 54, "5/15/2012",  "SOTREG"),
    ("22435",  "Autocar", "MAN", 42, "5/15/2012",  "SOTREG"),
    ("22436",  "Autocar", "MAN", 42, "5/15/2012",  "SOTREG"),
    ("22437",  "Autocar", "MAN", 54, "5/15/2012",  "SOTREG"),
    ("22438",  "Autocar", "MAN", 54, "5/15/2012",  "SOTREG"),
    ("22439",  "Autocar", "MAN", 42, "5/15/2012",  "SOTREG"),
    ("22441",  "Autocar", "MAN", 42, "5/18/2012",  "SOTREG"),
    ("22443",  "Autocar", "MAN", 54, "6/14/2012",  "SOTREG"),
    ("22446",  "Autocar", "MAN", 54, "6/14/2012",  "SOTREG"),
    ("22447",  "Autocar", "MAN", 42, "6/14/2012",  "SOTREG"),
    ("22448",  "Autocar", "MAN", 54, "6/14/2012",  "SOTREG"),
    ("22455",  "Autocar", "MAN", 42, "6/13/2012",  "SOTREG"),
    ("22462",  "Autocar", "MAN", 54, "8/1/2012",   "SOTREG"),
    ("22465",  "Autocar", "MAN", 42, "9/18/2012",  "SOTREG"),
    ("22466",  "Autocar", "MAN", 54, "9/18/2012",  "SOTREG"),
    ("22467",  "Autocar", "MAN", 54, "9/18/2012",  "SOTREG"),
    ("22471",  "Autocar", "MAN", 42, "9/19/2012",  "SOTREG"),
    ("22472",  "Autocar", "MAN", 42, "9/19/2012",  "SOTREG"),
    ("22473",  "Autocar", "MAN", 42, "10/5/2012",  "SOTREG"),
    ("22474",  "Autocar", "MAN", 54, "10/8/2012",  "SOTREG"),
    ("22477",  "Autocar", "MAN", 42, "11/5/2012",  "SOTREG"),
    ("22478",  "Autocar", "MAN", 54, "10/23/2012", "SOTREG"),
    ("22479",  "Autocar", "MAN", 42, "11/5/2012",  "SOTREG"),
    ("22481",  "Autocar", "MAN", 42, "11/5/2012",  "SOTREG"),
    ("22483",  "Autocar", "MAN", 42, "11/2/2012",  "SOTREG"),
    # ── SOTREG — Minibus Hyundai ──────────────────────────────────────────────
    ("22320",  "Minibus", "Hyundai", 17, "9/22/2006", "SOTREG"),
    ("22324",  "Minibus", "Hyundai", 17, "9/22/2006", "SOTREG"),
    ("22333",  "Minibus", "Hyundai", 17, "9/22/2006", "SOTREG"),
    ("22339",  "Minibus", "Hyundai", 17, "9/22/2006", "SOTREG"),
    # ── S/TOURISME — Autocars ─────────────────────────────────────────────────
    ("44105-A-14", "Autocar", "Volvo", 48, "9/15/2017",  "S/TOURISME"),
    ("56046-A-14", "Autocar", "Volvo", 48, "10/28/2020", "S/TOURISME"),
    ("56148-A-14", "Autocar", "MAN",   48, "11/28/2020", "S/TOURISME"),
    ("56151-A-14", "Autocar", "MAN",   48, "11/25/2020", "S/TOURISME"),
    ("61845-A-14", "Autocar", "MAN",   54, "10/11/2022", "S/TOURISME"),
    ("61846-A-14", "Autocar", "MAN",   54, "5/6/2022",   "S/TOURISME"),
    ("61847-A-15", "Autocar", "MAN",   54, "5/6/2022",   "S/TOURISME"),
    ("61848-A-15", "Autocar", "MAN",   55, "5/6/2022",   "S/TOURISME"),
    ("61858-A-14", "Autocar", "MAN",   54, "5/6/2022",   "S/TOURISME"),
    ("63321-A-14", "Autocar", "MAN",   54, "11/10/2022", "S/TOURISME"),
    ("63323-A-14", "Autocar", "MAN",   54, "11/10/2022", "S/TOURISME"),
    ("63325-A-14", "Autocar", "MAN",   54, "10/11/2022", "S/TOURISME"),
    ("64362-A-14", "Autocar", "MAN",   54, "2/14/2023",  "S/TOURISME"),
    # ── STCR — Autocars ───────────────────────────────────────────────────────
    ("77839-A-13", "Autocar", "Volvo", 54, "10/12/2022", "STCR"),
    ("78234-A-13", "Autocar", "Volvo", 48, "11/9/2022",  "STCR"),
    ("79142-A-13", "Autocar", "Volvo", 48, "2/14/2023",  "STCR"),
    ("79143-A-13", "Autocar", "Volvo", 48, "2/14/2023",  "STCR"),
    ("79401-A-13", "Autocar", "Volvo", 48, "3/13/2023",  "STCR"),
    ("82195-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82197-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82198-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82199-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82516-A-16", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82517-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82519-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82520-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    # ── MANAVETTE — Minibus Ford ─────────────────────────────────────────────
    ("65405-A-11", "Minibus", "Ford", 17, "1/8/2024",  "MANAVETTE"),
    ("65408-A-11", "Minibus", "Ford", 17, "1/8/2024",  "MANAVETTE"),
    ("65409-A-11", "Minibus", "Ford", 17, "1/8/2024",  "MANAVETTE"),
    ("65410-A-11", "Minibus", "Ford", 17, "1/8/2024",  "MANAVETTE"),
    ("65411-A-11", "Minibus", "Ford", 17, "1/8/2024",  "MANAVETTE"),
    ("65659-A-11", "Minibus", "Ford", 17, "8/1/2024",  "MANAVETTE"),
    # ── STCR — Minibus Hyundai ────────────────────────────────────────────────
    ("79402-A-13", "Minibus", "Hyundai",  17, "3/13/2023", "STCR"),
    ("79636-A-13", "Minibus", "Hyundai",  17, "3/17/2023", "STCR"),
    ("79637-A-13", "Minibus", "Hyundai",  17, "3/17/2023", "STCR"),
    ("79644-A-13", "Minibus", "Hyundai",  17, "3/20/2023", "STCR"),
    ("79795-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79796-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79805-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79806-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79826-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    # ── STCR — Minibus Mercedes ───────────────────────────────────────────────
    ("84112-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    ("84113-A-13", "Minibus", "Mercedes", 20, "3/14/2024", "STCR"),
    ("84114-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    ("84116-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    ("84118-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    # ── S/TOURISME — Mini-car Isuzu ───────────────────────────────────────────
    ("63689-A-14", "Mini-car", "Isuzu", 30, "11/7/2022", "S/TOURISME"),
    ("63690-A-14", "Mini-car", "Isuzu", 30, "11/7/2022", "S/TOURISME"),
    ("64025-A-14", "Mini-car", "Isuzu", 30, "11/7/2022", "S/TOURISME"),
    ("64026-A-13", "Mini-car", "Isuzu", 30, "11/7/2022", "S/TOURISME"),
    ("65382-A-14", "Mini-car", "Isuzu", 30, "5/26/2023", "S/TOURISME"),
    # ── STCR — Mini-car Isuzu ─────────────────────────────────────────────────
    ("77753-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77754-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77755-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77756-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77757-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    # ── CTM — Autocars Volvo ─────────────────────────────────────────────────
    ("70939-A-13", "Autocar", "Volvo", 48, "4/12/2021", "CTM"),
    ("70944-A-13", "Autocar", "Volvo", 48, "4/12/2021", "CTM"),
    ("70945-A-13", "Autocar", "Volvo", 48, "4/12/2021", "CTM"),
    ("70951-A-13", "Autocar", "Volvo", 48, "4/12/2021", "CTM"),
    ("70953-A-13", "Autocar", "Volvo", 48, "4/12/2021", "CTM"),
]
# fmt: on

assert len(VEHICLES) == 106, f"Expected 106 vehicles, got {len(VEHICLES)}"


async def seed():
    conn = await asyncpg.connect(DB_URL)
    tenant_id = await conn.fetchval("SELECT id FROM tenant LIMIT 1")
    site_kh   = await conn.fetchval("SELECT id FROM site WHERE code = 'S01'")
    print(f"Tenant: {tenant_id}  |  Site S01: {site_kh}")

    deleted = await conn.execute("DELETE FROM vehicle WHERE tenant_id = $1", tenant_id)
    print(f"Cleared: {deleted}")

    inserted = 0
    for mat, vtype, brand, cap, circ_str, owner in VEHICLES:
        circ = d(circ_str)
        if owner == "SOTREG":
            owner_type  = "SOTREG"
            prestataire = None
            site_id     = site_kh
        else:
            owner_type  = "Prestataire"
            prestataire = owner
            site_id     = None

        await conn.execute(
            """
            INSERT INTO vehicle (
                id, tenant_id, matricule, type, brand_model, capacity,
                year, circulation_date, owner_type, prestataire,
                site_id, condition, zfe_compliant, is_pmr_accessible
            ) VALUES (
                gen_random_uuid(), $1, $2, $3, $4, $5,
                $6, $7, $8, $9,
                $10, 'Bon', false, false
            )
            """,
            tenant_id, mat, vtype, brand, cap,
            circ.year, circ, owner_type, prestataire, site_id,
        )
        inserted += 1

    await conn.close()

    print(f"\nInserted: {inserted} vehicles")
    owners: dict[str, int] = {}
    for row in VEHICLES:
        owners[row[5]] = owners.get(row[5], 0) + 1
    for k, v in sorted(owners.items()):
        print(f"  {k:<15}: {v}")


if __name__ == "__main__":
    asyncio.run(seed())
