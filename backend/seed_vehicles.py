"""
Seed script — Parc Véhicule SOTREG
Inserts real fleet data extracted from the Parc Véhicule spreadsheet.
Run from the backend/ directory:  python seed_vehicles.py
"""

import asyncio
import asyncpg
from datetime import date

DB_URL = "postgresql://postgres:password@helium:5432/heliumdb"

# ── helpers ──────────────────────────────────────────────────────────────────
def d(s: str) -> date:
    """Parse M/D/YYYY → date."""
    m, day, y = s.split("/")
    return date(int(y), int(m), int(day))

# ── raw fleet data ────────────────────────────────────────────────────────────
# Columns: matricule, type, brand_model, capacity, circulation_date_str, owner
VEHICLES = [
    # ── SOTREG — Autocars MAN 54 places ──────────────────────────────────────
    ("22363",  "Autocar", "MAN",       54, "9/30/2011", "SOTREG"),
    ("22401",  "Autocar", "MAN",       54, "1/18/2012", "SOTREG"),
    ("22405",  "Autocar", "MAN",       54, "1/18/2012", "SOTREG"),
    ("22410",  "Autocar", "MAN",       54, "3/19/2012", "SOTREG"),
    ("22420",  "Autocar", "MAN",       54, "2/17/2012", "SOTREG"),
    ("22421",  "Autocar", "MAN",       54, "2/17/2012", "SOTREG"),
    ("22422",  "Autocar", "MAN",       54, "2/17/2012", "SOTREG"),
    ("22423",  "Autocar", "MAN",       54, "2/17/2012", "SOTREG"),
    ("22424",  "Autocar", "MAN",       54, "2/17/2012", "SOTREG"),
    ("22425",  "Autocar", "MAN",       54, "3/22/2012", "SOTREG"),
    ("22426",  "Autocar", "MAN",       54, "3/22/2012", "SOTREG"),
    ("22430",  "Autocar", "MAN",       54, "3/22/2012", "SOTREG"),
    ("22434",  "Autocar", "MAN",       54, "5/15/2012", "SOTREG"),
    ("22435",  "Autocar", "MAN",       54, "5/15/2012", "SOTREG"),
    ("22437",  "Autocar", "MAN",       54, "5/15/2012", "SOTREG"),
    ("22438",  "Autocar", "MAN",       54, "5/15/2012", "SOTREG"),
    ("22441",  "Autocar", "MAN",       54, "5/18/2012", "SOTREG"),
    ("22448",  "Autocar", "MAN",       54, "6/14/2012", "SOTREG"),
    ("22455",  "Autocar", "MAN",       54, "6/14/2012", "SOTREG"),
    ("22462",  "Autocar", "MAN",       54, "8/1/2012",  "SOTREG"),
    ("22466",  "Autocar", "MAN",       54, "9/18/2012", "SOTREG"),
    ("22471",  "Autocar", "MAN",       54, "9/18/2012", "SOTREG"),
    # ── SOTREG — Autocars MAN 42 places ──────────────────────────────────────
    ("22427",  "Autocar", "MAN",       42, "3/22/2012", "SOTREG"),
    ("22428",  "Autocar", "MAN",       42, "3/22/2012", "SOTREG"),
    ("22431",  "Autocar", "MAN",       42, "5/15/2012", "SOTREG"),
    ("22432",  "Autocar", "MAN",       42, "5/15/2012", "SOTREG"),
    ("22433",  "Autocar", "MAN",       42, "5/15/2012", "SOTREG"),
    ("22436",  "Autocar", "MAN",       42, "5/15/2012", "SOTREG"),
    ("22443",  "Autocar", "MAN",       42, "6/14/2012", "SOTREG"),
    ("22447",  "Autocar", "MAN",       42, "6/14/2012", "SOTREG"),
    ("22467",  "Autocar", "MAN",       42, "9/18/2012", "SOTREG"),
    ("22472",  "Autocar", "MAN",       42, "9/19/2012", "SOTREG"),
    ("22473",  "Autocar", "MAN",       42, "9/19/2012", "SOTREG"),
    ("22474",  "Autocar", "MAN",       42, "10/5/2012", "SOTREG"),
    ("22477",  "Autocar", "MAN",       42, "11/5/2012", "SOTREG"),
    ("22478",  "Autocar", "MAN",       42, "10/23/2012","SOTREG"),
    ("22479",  "Autocar", "MAN",       42, "10/5/2012", "SOTREG"),
    ("22481",  "Autocar", "MAN",       42, "11/5/2012", "SOTREG"),
    ("22482",  "Autocar", "MAN",       42, "11/2/2012", "SOTREG"),
    # ── SOTREG — Minibus Hyundai 17 places ───────────────────────────────────
    ("22324",  "Minibus", "Hyundai",   17, "9/22/2006", "SOTREG"),
    ("22333",  "Minibus", "Hyundai",   17, "9/22/2006", "SOTREG"),
    ("22338",  "Minibus", "Hyundai",   17, "9/22/2006", "SOTREG"),
    ("22339",  "Minibus", "Hyundai",   17, "9/22/2006", "SOTREG"),
    # ── S'TOURISME — Autocars ─────────────────────────────────────────────────
    ("44105-A-14", "Autocar", "Volvo", 48, "9/15/2017",  "S'TOURISME"),
    ("56046-A-14", "Autocar", "MAN",   48, "2/28/2020",  "S'TOURISME"),
    ("56151-A-14", "Autocar", "MAN",   48, "11/25/2020", "S'TOURISME"),
    ("57052-A-14", "Autocar", "MAN",   48, "9/11/2020",  "S'TOURISME"),
    ("61846-A-14", "Autocar", "MAN",   54, "5/6/2022",   "S'TOURISME"),
    ("63321-A-14", "Autocar", "MAN",   54, "11/10/2022", "S'TOURISME"),
    ("63323-A-14", "Autocar", "MAN",   54, "11/10/2022", "S'TOURISME"),
    ("64362-A-14", "Autocar", "MAN",   54, "2/14/2023",  "S'TOURISME"),
    ("78639-A-14", "Autocar", "Volvo", 48, "2/14/2023",  "S'TOURISME"),
    # ── S'TOURISME — Mini-cars ────────────────────────────────────────────────
    ("63689-A-14", "Mini-car", "Isuzu", 30, "11/7/2022", "S'TOURISME"),
    ("64025-A-14", "Mini-car", "Isuzu", 30, "11/7/2022", "S'TOURISME"),
    ("65382-A-14", "Mini-car", "Isuzu", 30, "5/26/2022", "S'TOURISME"),
    # ── STCR — Autocars ───────────────────────────────────────────────────────
    ("77234-A-14", "Autocar", "Volvo", 48, "11/9/2023",  "STCR"),
    ("79142-A-13", "Autocar", "Volvo", 48, "2/14/2023",  "STCR"),
    ("79143-A-13", "Autocar", "MAN",   48, "3/14/2023",  "STCR"),
    ("82195-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82197-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82198-A-13", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82199-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82516-A-16", "Autocar", "MAN",   48, "10/2/2023",  "STCR"),
    ("82517-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82519-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    ("82520-A-13", "Autocar", "MAN",   48, "11/21/2023", "STCR"),
    # ── STCR — Minibus Hyundai ────────────────────────────────────────────────
    ("79636-A-13", "Minibus", "Hyundai",  17, "3/17/2023", "STCR"),
    ("79637-A-13", "Minibus", "Hyundai",  17, "3/17/2023", "STCR"),
    ("79638-A-13", "Minibus", "Hyundai",  17, "3/17/2023", "STCR"),
    ("79795-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79806-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    ("79828-A-13", "Minibus", "Hyundai",  17, "3/24/2023", "STCR"),
    # ── STCR — Minibus Mercedes ───────────────────────────────────────────────
    ("84113-A-13", "Minibus", "Mercedes", 20, "3/14/2024", "STCR"),
    ("84114-A-13", "Minibus", "Mercedes", 20, "3/14/2024", "STCR"),
    ("84117-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    ("84118-A-13", "Minibus", "Mercedes", 20, "3/13/2024", "STCR"),
    # ── STCR — Mini-cars Isuzu ────────────────────────────────────────────────
    ("77753-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77754-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77755-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77756-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    ("77757-A-13", "Mini-car", "Isuzu", 30, "10/5/2022", "STCR"),
    # ── MANAVETTE — Minibus Ford ─────────────────────────────────────────────
    ("71905-A-13", "Minibus", "Ford",   17, "5/8/2022",  "MANAVETTE"),
    ("65408-A-11", "Minibus", "Ford",   17, "1/8/2024",  "MANAVETTE"),
    ("65409-A-11", "Minibus", "Ford",   17, "1/8/2024",  "MANAVETTE"),
    ("65410-A-11", "Minibus", "Ford",   17, "8/1/2024",  "MANAVETTE"),
    ("65411-A-11", "Minibus", "Ford",   17, "8/1/2024",  "MANAVETTE"),
    ("65659-A-11", "Minibus", "Ford",   17, "8/1/2024",  "MANAVETTE"),
    # ── CTM — Autocars Volvo ─────────────────────────────────────────────────
    ("70939-A-13", "Autocar", "Volvo",  48, "4/12/2021", "CTM"),
    ("70944-A-13", "Autocar", "Volvo",  48, "4/12/2021", "CTM"),
    ("70951-A-13", "Autocar", "Volvo",  48, "4/12/2021", "CTM"),
    ("70953-A-13", "Autocar", "Volvo",  48, "4/12/2021", "CTM"),
]


async def seed():
    conn = await asyncpg.connect(DB_URL)

    # Tenant
    tenant_id = await conn.fetchval("SELECT id FROM tenant LIMIT 1")
    print(f"Tenant: {tenant_id}")

    # Main site (Khouribga) for SOTREG-owned vehicles
    site_kh = await conn.fetchval("SELECT id FROM site WHERE code = 'S01'")
    print(f"Site S01: {site_kh}")

    # Clear existing demo vehicles (keep none, start fresh)
    deleted = await conn.execute("DELETE FROM vehicle WHERE tenant_id = $1", tenant_id)
    print(f"Cleared: {deleted}")

    inserted = 0
    skipped = 0

    for matricule, vtype, brand, capacity, circ_str, owner in VEHICLES:
        circ_date = d(circ_str)
        yr = circ_date.year

        # owner_type and prestataire
        if owner == "SOTREG":
            owner_type = "SOTREG"
            prestataire = None
            site_id = site_kh  # SOTREG vehicles assigned to main Khouribga garage
        else:
            owner_type = "Prestataire"
            prestataire = owner
            site_id = None  # External vehicles not site-assigned

        try:
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
                ON CONFLICT DO NOTHING
                """,
                tenant_id, matricule, vtype, brand, capacity,
                yr, circ_date, owner_type, prestataire,
                site_id,
            )
            inserted += 1
        except Exception as e:
            print(f"  SKIP {matricule}: {e}")
            skipped += 1

    await conn.close()
    print(f"\nDone — {inserted} inserted, {skipped} skipped")
    print(f"Breakdown by owner:")
    owners = {}
    for row in VEHICLES:
        owners[row[5]] = owners.get(row[5], 0) + 1
    for k, v in sorted(owners.items()):
        print(f"  {k}: {v} vehicles")


if __name__ == "__main__":
    asyncio.run(seed())
