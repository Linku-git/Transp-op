"""Sage HR field mapping to Transpop Employee model."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SAGE_FIELD_MAP: dict[str, str] = {
    "matricule": "matricule",
    "prenom": "first_name",
    "nom": "last_name",
    "email_pro": "email",
    "telephone": "phone",
    "service": "department",
    "poste": "job_title",
    "date_entree": "hire_date",
    "equipe": "shift_time",
    "etablissement": "site_name",
    "date_modification": "modified_at",
}

SAGE_DEPARTMENT_MAP: dict[str, str] = {
    "SRV_PROD": "Production",
    "SRV_LOG": "Logistique",
    "SRV_MAINT": "Maintenance",
    "SRV_ADM": "Administration",
    "SRV_RH": "Ressources Humaines",
    "SRV_INFO": "Informatique",
}

SAGE_SHIFT_MAP: dict[str, str] = {
    "EQ_MATIN": "Équipe Matin",
    "EQ_APREM": "Équipe Après-midi",
    "EQ_NUIT": "Équipe Nuit",
    "EQ_NORM": "Normal",
}


def parse_sage_date(value: str | None) -> str | None:
    if not value:
        return None
    # Sage uses dd/mm/yyyy or ISO format
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(str(value), fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        logger.warning("Could not parse Sage date: %s", value)
        return None


def map_sage_employee(sage_record: dict) -> dict:
    result: dict = {}
    for sage_field, transpop_field in SAGE_FIELD_MAP.items():
        value = sage_record.get(sage_field)
        if value is None:
            continue
        if sage_field in ("date_entree", "date_modification"):
            result[transpop_field] = parse_sage_date(str(value))
        elif sage_field == "service":
            result[transpop_field] = SAGE_DEPARTMENT_MAP.get(str(value), str(value))
        elif sage_field == "equipe":
            result[transpop_field] = SAGE_SHIFT_MAP.get(str(value), str(value))
        else:
            result[transpop_field] = str(value)

    # Payroll data (nested)
    payroll = sage_record.get("bulletinPaie") or sage_record.get("payroll")
    if isinstance(payroll, dict):
        result["payroll_data"] = {
            "gross_salary": payroll.get("salaire_brut"),
            "net_salary": payroll.get("salaire_net"),
            "transport_allowance": payroll.get("indemnite_transport"),
            "period": payroll.get("periode"),
        }

    return result
