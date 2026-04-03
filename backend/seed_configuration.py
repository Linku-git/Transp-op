"""Seed configuration plan + 591 transport rows from XLSX."""
from __future__ import annotations

import asyncio
import datetime
import os
import sys
import uuid

import asyncpg
import openpyxl

XLSX_PATH = os.path.join(os.path.dirname(__file__), "..", "attached_assets", "config_1775180737219.xlsx")
DATABASE_URL = "postgresql://postgres:password@helium:5432/heliumdb"
TENANT_ID = "0cea9745-6aa2-4105-9bdc-341d95999048"

SECTEUR_TO_SITE: dict[str, str | None] = {}


def fmt_time(t: object) -> str | None:
    if t is None:
        return None
    if isinstance(t, datetime.time):
        return t.strftime("%H:%M")
    if isinstance(t, datetime.datetime):
        return t.strftime("%H:%M")
    s = str(t).strip()
    if not s or s.lower() in ("none", "nan"):
        return None
    return s


def to_int_minutes(t: object) -> int | None:
    if t is None:
        return None
    if isinstance(t, datetime.time):
        return t.hour * 60 + t.minute
    return None


def to_float(v: object) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


async def main() -> None:
    conn = await asyncpg.connect(DATABASE_URL)

    # ── 0. Build secteur → site_id map ────────────────────────────────────
    sites = await conn.fetch(
        "SELECT id, code, name FROM site WHERE tenant_id=$1", uuid.UUID(TENANT_ID)
    )
    # Map by known secteur names to site codes
    SECTEUR_SITE_CODE = {
        "KHOURIBGA": "S01",
        "BOULANOIR": "S01",
        "BOUJNIBA": "S01",
        "HATTANE": "S01",
        "OUEDZEM": "S03",
        "FQUIH BEN SALEH": "S02",
    }
    code_to_id = {s["code"]: str(s["id"]) for s in sites}
    for sect, code in SECTEUR_SITE_CODE.items():
        SECTEUR_TO_SITE[sect] = code_to_id.get(code)

    # ── 1. Remove existing "current" plan to avoid duplicate ───────────────
    await conn.execute(
        """DELETE FROM configuration_transport ct
           USING configuration_plan cp
           WHERE ct.plan_id = cp.id
             AND cp.tenant_id=$1 AND cp.source='seed'""",
        uuid.UUID(TENANT_ID),
    )
    await conn.execute(
        "DELETE FROM configuration_plan WHERE tenant_id=$1 AND source='seed'",
        uuid.UUID(TENANT_ID),
    )

    # ── 2. Create plan ─────────────────────────────────────────────────────
    plan_id = uuid.uuid4()
    await conn.execute(
        """INSERT INTO configuration_plan (id, tenant_id, name, description, is_active, is_current, source)
           VALUES ($1, $2, $3, $4, true, true, 'seed')""",
        plan_id,
        uuid.UUID(TENANT_ID),
        "Configuration Initiale 2024",
        "Configuration de transport initiale importée depuis le fichier de référence (591 lignes)",
    )
    print(f"Created plan: {plan_id}")

    # ── 3. Load XLSX ───────────────────────────────────────────────────────
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    data_rows = rows[1:]  # skip header
    print(f"Loaded {len(data_rows)} rows from XLSX")

    # ── 4. Insert rows ─────────────────────────────────────────────────────
    records = []
    for r in data_rows:
        conducteur = str(r[0]).strip() if r[0] is not None else None
        poste = str(r[1]).strip() if r[1] is not None else None
        prestataire = str(r[2]).strip() if r[2] is not None else None
        mle_vehicule = str(r[3]).strip() if r[3] is not None else None
        type_vehicule = str(r[4]).strip() if r[4] is not None else None
        type_moteur = str(r[5]).strip() if r[5] is not None else None
        secteur = str(r[6]).strip() if r[6] is not None else None
        entite = str(r[7]).strip() if r[7] is not None else None
        aller_retour = str(r[8]).strip() if r[8] is not None else None
        shift = str(r[9]).strip() if r[9] is not None else None
        heure_depart = fmt_time(r[10])
        point_depart = str(r[11]).strip() if r[11] is not None else None
        point_arrivee = str(r[12]).strip() if r[12] is not None else None
        heure_arrivee = fmt_time(r[13])
        arrets_circuit = str(r[14]).strip() if r[14] is not None else None
        duree_trajet_min = to_int_minutes(r[15])
        km = to_float(r[16])
        rot = to_float(r[17])
        t_km = to_float(r[18])

        site_id_str = SECTEUR_TO_SITE.get(secteur) if secteur else None
        site_id = uuid.UUID(site_id_str) if site_id_str else None

        records.append((
            uuid.uuid4(),
            uuid.UUID(TENANT_ID),
            plan_id,
            site_id,
            conducteur, poste, prestataire, mle_vehicule,
            type_vehicule, type_moteur, secteur, entite,
            aller_retour, shift,
            heure_depart, point_depart, point_arrivee, heure_arrivee,
            arrets_circuit, duree_trajet_min, km, rot, t_km,
            True,
        ))

    await conn.executemany(
        """INSERT INTO configuration_transport (
            id, tenant_id, plan_id, site_id,
            conducteur, poste, prestataire, mle_vehicule,
            type_vehicule, type_moteur, secteur, entite,
            aller_retour, shift,
            heure_depart, point_depart, point_arrivee, heure_arrivee,
            arrets_circuit, duree_trajet_min, km, rot, t_km,
            is_active
        ) VALUES (
            $1, $2, $3, $4,
            $5, $6, $7, $8,
            $9, $10, $11, $12,
            $13, $14,
            $15, $16, $17, $18,
            $19, $20, $21, $22, $23,
            $24
        )""",
        records,
    )

    print(f"Inserted {len(records)} configuration transport rows")
    await conn.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
