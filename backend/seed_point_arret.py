"""
Seed script — Points d'Arrêt SOTREG (58 arrêts, données exactes)
Run from backend/ directory:  python seed_point_arret.py
"""
import asyncio
import asyncpg

DB_URL = "postgresql://postgres:password@helium:5432/heliumdb"

# fmt: off
# (code, nom, lat, lng, ville, correspondance_tb)
STOPS = [
    # ── KHOURIBGA ──────────────────────────────────────────────────────────────
    ("KH01",  "HAMROUKAT1",                         32.8977513, -6.9078049, "Khouribga", "H"),
    ("KH02",  "HAMROUKAT2",                         32.8970871, -6.9031150, "Khouribga", "H"),
    ("KH03",  "HAMROUKAT3",                         32.8966001, -6.8992711, "Khouribga", None),
    ("KH04",  "TITANIC",                            32.8925012, -6.8943217, "Khouribga", "T"),
    ("KH05",  "AL MASSIRA",                         32.8873482, -6.8990454, "Khouribga", "1"),
    ("KH06",  "NAHDA",                              32.8858381, -6.9057054, "Khouribga", "2"),
    ("KH07",  "LAADOULAT",                          32.8883051, -6.9181398, "Khouribga", "3"),
    ("KH08",  "ONEP",                               32.8904708, -6.9276843, "Khouribga", "Q1"),
    ("KH09",  "CAFE WARDA",                         32.8919377, -6.9338923, "Khouribga", "Q2"),
    ("KH10",  "AVOLA",                              32.8975878, -6.9330748, "Khouribga", "Q3"),
    ("KH11",  "Pharmacie Attraoui",                 32.8973972, -6.9395981, "Khouribga", "Q4"),
    ("KH12",  "Pharmacie Ouafae (Marjane Market)",  32.8987787, -6.9363085, "Khouribga", "Q5"),
    ("KH13",  "RABBANI",                            32.8930183, -6.9379905, "Khouribga", "Q6"),
    ("KH14",  "ECOLE AMAL",                         32.8910860, -6.9340732, "Khouribga", "Q7"),
    ("KH15",  "MOSQUE QODS",                        32.8860129, -6.9310167, "Khouribga", "Q8"),
    ("KH16",  "ROUDANI",                            32.8845079, -6.9208855, "Khouribga", "4"),
    ("KH17",  "IMARA",                              32.8736050, -6.9244020, "Khouribga", "IMARA"),
    ("KH18",  "KHOUADRIA",                          32.8789325, -6.9199215, "Khouribga", "5"),
    ("KH19",  "BELLE ILE",                          32.8778011, -6.9167160, "Khouribga", "6"),
    ("KH20",  "KASSOU",                             32.8731463, -6.9169585, "Khouribga", "7"),
    ("KH21",  "BARIGOU",                            32.8743092, -6.9118776, "Khouribga", "8"),
    ("KH22",  "GOUTE DE LAIT",                      32.8772010, -6.9107695, "Khouribga", "9"),
    ("KH23",  "LA PISCINE",                         32.8756811, -6.9054707, "Khouribga", "10"),
    ("KH24",  "CFO",                                32.8799843, -6.9010458, "Khouribga", "11"),
    ("KH25",  "LA FACULTE",                         32.8681224, -6.9068366, "Khouribga", "Z"),
    ("KH26",  "LA FERME",                           32.8619610, -6.9078155, "Khouribga", "F"),
    ("KH27",  "OUM KORA",                           32.8682220, -6.9162440, "Khouribga", "OK"),
    # ── BOLANOUIR ──────────────────────────────────────────────────────────────
    ("BL01",  "HAMAM OCP",                          32.8518470, -6.8763768, "Bolanouir", None),
    ("BL02",  "CHEF VILLAGE",                       32.8554409, -6.8778762, "Bolanouir", None),
    ("BL03",  "LA PISCINE",                         32.8625471, -6.8782838, "Bolanouir", None),
    ("BL04",  "EL MONTALAQ",                        32.8600485, -6.8739306, "Bolanouir", None),
    # ── BOUJNIBA ───────────────────────────────────────────────────────────────
    ("BJ01",  "station",                            32.9060757, -6.7829419, "Boujniba",  None),
    ("BJ02",  "pharmacie Ihssan",                   32.9019261, -6.7816601, "Boujniba",  None),
    ("BJ03",  "châteaux d'eau",                     32.9011800, -6.7727951, "Boujniba",  None),
    ("BJ04",  "hammam Saadâ",                       32.8952930, -6.7755900, "Boujniba",  None),
    ("BJ05",  "gendarme de bj",                     32.8957806, -6.7755766, "Boujniba",  None),
    ("BJ06",  "poste Bank - et l'hopital",          32.8978638, -6.7778887, "Boujniba",  None),
    ("BJ07",  "wafa Bank",                          32.8994110, -6.7816303, "Boujniba",  None),
    ("BJ08",  "collège Khalid ben Walid",           32.8958121, -6.7810724, "Boujniba",  None),
    # ── HATTANE ────────────────────────────────────────────────────────────────
    ("HT01",  "Sbata 1 château de l'eau",           32.8437162, -6.7999096, "Hattane",   None),
    ("HT02",  "Sbata 2 mosquée",                    32.8383618, -6.8037452, "Hattane",   None),
    ("HT03",  "gandarme de hat",                    32.8376294, -6.8066581, "Hattane",   None),
    # ── BIR MEZOUI ─────────────────────────────────────────────────────────────
    ("BM01",  "Mosquée",                            32.9024908, -6.6812160, "Bir Mezoui",None),
    ("BM02",  "A côté du Rond-point",               32.9013181, -6.6784297, "Bir Mezoui",None),
    # ── GUEFFAF ────────────────────────────────────────────────────────────────
    ("GF01",  "A proximité de CHEMIN DE FER",       32.9202721, -6.7192734, "Gueffaf",   None),
    ("GF02",  "KIYADA",                             32.9229051, -6.7178315, "Gueffaf",   None),
    # ── OUED ZEM ───────────────────────────────────────────────────────────────
    ("OZ01",  "BANANA",                             32.8625064, -6.5812701, "Oued Zem",  None),
    ("OZ02",  "PHARMACIE NOUR",                     32.8558643, -6.5794193, "Oued Zem",  None),
    ("OZ03",  "SOUK",                               32.8547648, -6.5773701, "Oued Zem",  None),
    ("OZ04",  "AIN BARTI",                          32.8532777, -6.5739262, "Oued Zem",  None),
    ("OZ05",  "ISTA",                               32.8549450, -6.5687871, "Oued Zem",  None),
    ("OZ06",  "AL BOUSTAN",                         32.8594030, -6.5524798, "Oued Zem",  None),
    ("OZ07",  "AL HASANIA",                         32.8600461, -6.5562665, "Oued Zem",  None),
    ("OZ08",  "BRACH",                              32.8623081, -6.5660727, "Oued Zem",  None),
    ("OZ09",  "CHAABI",                             32.8631643, -6.5699887, "Oued Zem",  None),
    ("OZ10",  "TANJI",                              32.8646152, -6.5763724, "Oued Zem",  None),
    ("OZ11",  "VILLAGE",                            32.8655208, -6.5802830, "Oued Zem",  None),
    ("OZ12",  "KORAIA",                             32.8648292, -6.5814002, "Oued Zem",  None),
]
# fmt: on

assert len(STOPS) == 58, f"Expected 58 stops, got {len(STOPS)}"


async def seed():
    conn = await asyncpg.connect(DB_URL)

    tenant_id = await conn.fetchval("SELECT id FROM tenant LIMIT 1")
    site_kh   = await conn.fetchval("SELECT id FROM site WHERE code = 'S01'")
    site_oz   = await conn.fetchval("SELECT id FROM site WHERE code = 'S03'")
    print(f"Tenant: {tenant_id}")
    print(f"Site S01 (Khouribga): {site_kh}")
    print(f"Site S03 (Oued Zem):  {site_oz}")

    deleted = await conn.execute("DELETE FROM point_arret WHERE tenant_id = $1", tenant_id)
    print(f"Cleared: {deleted}")

    by_ville: dict[str, int] = {}
    for code, nom, lat, lng, ville, corresp in STOPS:
        if "Khouribga" in ville:
            site_id = site_kh
        elif "Oued Zem" in ville:
            site_id = site_oz
        else:
            site_id = None

        await conn.execute(
            """
            INSERT INTO point_arret (
                id, tenant_id, site_id, code, nom, ville,
                lat, lng, prestataire, is_active, correspondance_tb
            ) VALUES (
                gen_random_uuid(), $1, $2, $3, $4, $5,
                $6, $7, 'SOTREG', true, $8
            )
            """,
            tenant_id, site_id, code, nom, ville,
            lat, lng, corresp,
        )
        by_ville[ville] = by_ville.get(ville, 0) + 1

    await conn.close()

    print(f"\nInserted: {sum(by_ville.values())} stops")
    for v, n in sorted(by_ville.items()):
        print(f"  {v:<15}: {n}")


if __name__ == "__main__":
    asyncio.run(seed())
