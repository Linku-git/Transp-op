"""Talentsoft field mapping to Transpop Employee model."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

TALENTSOFT_FIELD_MAP: dict[str, str] = {
    "employeeId": "matricule",
    "firstName": "first_name",
    "lastName": "last_name",
    "professionalEmail": "email",
    "mobilePhone": "phone",
    "organizationalUnit": "department",
    "jobTitle": "job_title",
    "entryDate": "hire_date",
    "workSchedule": "shift_time",
    "siteName": "site_name",
    "lastModifiedDate": "modified_at",
}

TALENTSOFT_DEPARTMENT_MAP: dict[str, str] = {
    "TS_PROD": "Production",
    "TS_LOG": "Logistique",
    "TS_MAINT": "Maintenance",
    "TS_ADMIN": "Administration",
    "TS_HR": "Ressources Humaines",
    "TS_IT": "Informatique",
}

TALENTSOFT_SCHEDULE_MAP: dict[str, str] = {
    "MATIN": "Équipe Matin",
    "APREM": "Équipe Après-midi",
    "NUIT": "Équipe Nuit",
    "NORMAL": "Normal",
}


def parse_talentsoft_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(str(value), "%d/%m/%Y")
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except (ValueError, TypeError):
            logger.warning("Could not parse Talentsoft date: %s", value)
            return None


def map_talentsoft_employee(ts_record: dict) -> dict:
    result: dict = {}
    for ts_field, transpop_field in TALENTSOFT_FIELD_MAP.items():
        value = ts_record.get(ts_field)
        if value is None:
            continue
        if ts_field in ("entryDate", "lastModifiedDate"):
            result[transpop_field] = parse_talentsoft_date(str(value))
        elif ts_field == "organizationalUnit":
            result[transpop_field] = TALENTSOFT_DEPARTMENT_MAP.get(str(value), str(value))
        elif ts_field == "workSchedule":
            result[transpop_field] = TALENTSOFT_SCHEDULE_MAP.get(str(value), str(value))
        else:
            result[transpop_field] = str(value)

    # Training data (nested)
    training = ts_record.get("trainingRecords") or ts_record.get("formations")
    if isinstance(training, list):
        result["training_records"] = [
            {
                "title": t.get("title", ""),
                "completed_at": parse_talentsoft_date(t.get("completionDate")),
                "score": t.get("score"),
            }
            for t in training
        ]

    return result
