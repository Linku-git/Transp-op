"""Workday field mapping to Transpop Employee model.

Maps Workday HCM API fields (Workers, Positions, Schedules) to internal model.
Handles Workday-specific formats: WID references, effective-dated records, XML/SOAP structures.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Workday Worker → Transpop Employee field mapping
WORKDAY_FIELD_MAP: dict[str, str] = {
    "Worker_ID": "matricule",
    "First_Name": "first_name",
    "Last_Name": "last_name",
    "Email_Address": "email",
    "Phone_Number": "phone",
    "Department_Name": "department",
    "Job_Title": "job_title",
    "Hire_Date": "hire_date",
    "Schedule_Name": "shift_time",
    "Location_Name": "site_name",
    "Worker_Status": "is_active",
    "Last_Modified": "modified_at",
}

# Workday department WID → Transpop department name
WORKDAY_DEPARTMENT_MAP: dict[str, str] = {
    "WD_DEP_PROD": "Production",
    "WD_DEP_LOG": "Logistique",
    "WD_DEP_MAINT": "Maintenance",
    "WD_DEP_ADMIN": "Administration",
    "WD_DEP_HR": "Ressources Humaines",
    "WD_DEP_IT": "Informatique",
    "WD_DEP_QUAL": "Qualité",
}

# Workday schedule WID → Transpop shift labels
WORKDAY_SCHEDULE_MAP: dict[str, str] = {
    "WD_SCH_MORNING": "Équipe Matin",
    "WD_SCH_AFTERNOON": "Équipe Après-midi",
    "WD_SCH_NIGHT": "Équipe Nuit",
    "WD_SCH_NORMAL": "Normal",
    "WD_SCH_FLEX": "Horaires Flexibles",
}

# Workday status values → boolean
WORKDAY_STATUS_MAP: dict[str, bool] = {
    "Active": True,
    "active": True,
    "Terminated": False,
    "terminated": False,
    "On_Leave": True,
    "on_leave": True,
    "Pre_Hire": False,
    "Retired": False,
}


def parse_workday_date(value: str | None) -> str | None:
    """Parse Workday date formats to ISO 8601.

    Workday uses:
    - ISO 8601: 2026-04-09T10:30:00Z
    - Date only: 2026-04-09
    - Datetime with offset: 2026-04-09T10:30:00.000-07:00
    """
    if not value:
        return None

    try:
        # Handle various ISO formats
        cleaned = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        return dt.isoformat()
    except (ValueError, TypeError):
        pass

    # Try date-only format
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except (ValueError, TypeError):
        logger.warning("Could not parse Workday date: %s", value)
        return None


def resolve_wid_reference(ref: dict | str | None) -> str | None:
    """Extract the actual value from a Workday WID reference object.

    Workday references look like:
    {"WID": "abc123", "Descriptor": "Human Resources"}
    or sometimes just a string.
    """
    if ref is None:
        return None
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        return ref.get("Descriptor") or ref.get("WID") or ref.get("ID")
    return str(ref)


def get_effective_record(records: list[dict], as_of: datetime | None = None) -> dict | None:
    """Get the effective-dated record for a given date.

    Workday uses effective dating — multiple records may exist for the same entity
    with different Effective_Date values. Returns the most recent one as of `as_of`.
    """
    if not records:
        return None

    target = as_of or datetime.now(timezone.utc)

    valid = []
    for record in records:
        eff_date_str = record.get("Effective_Date")
        if eff_date_str:
            try:
                eff_date = datetime.fromisoformat(
                    str(eff_date_str).replace("Z", "+00:00")
                )
                if eff_date <= target:
                    valid.append((eff_date, record))
            except (ValueError, TypeError):
                valid.append((datetime.min.replace(tzinfo=timezone.utc), record))
        else:
            valid.append((datetime.min.replace(tzinfo=timezone.utc), record))

    if not valid:
        return records[0] if records else None

    valid.sort(key=lambda x: x[0], reverse=True)
    return valid[0][1]


def map_workday_employee(wd_record: dict) -> dict:
    """Map a Workday Worker record to Transpop format.

    Args:
        wd_record: Raw record from Workday HCM API

    Returns:
        Dict with Transpop Employee field names.
    """
    result: dict = {}

    for wd_field, transpop_field in WORKDAY_FIELD_MAP.items():
        value = wd_record.get(wd_field)
        if value is None:
            continue

        # Resolve WID references
        if isinstance(value, dict) and ("WID" in value or "Descriptor" in value):
            value = resolve_wid_reference(value)

        # Apply field-specific transformations
        if wd_field in ("Hire_Date", "Last_Modified"):
            result[transpop_field] = parse_workday_date(str(value))
        elif wd_field == "Department_Name":
            resolved = str(value)
            result[transpop_field] = WORKDAY_DEPARTMENT_MAP.get(resolved, resolved)
        elif wd_field == "Schedule_Name":
            resolved = str(value)
            result[transpop_field] = WORKDAY_SCHEDULE_MAP.get(resolved, resolved)
        elif wd_field == "Worker_Status":
            result[transpop_field] = WORKDAY_STATUS_MAP.get(str(value), True)
        else:
            result[transpop_field] = str(value)

    # Handle nested position data
    position = wd_record.get("Position_Data") or wd_record.get("position")
    if isinstance(position, dict):
        if "Job_Title" in position:
            result["job_title"] = resolve_wid_reference(position["Job_Title"]) or ""
        if "Location" in position:
            result["site_name"] = resolve_wid_reference(position["Location"]) or ""

    # Handle nested contact data
    contact = wd_record.get("Contact_Data") or wd_record.get("contact")
    if isinstance(contact, dict):
        if "Email_Address" in contact:
            result["email"] = str(contact["Email_Address"])
        if "Phone_Number" in contact:
            result["phone"] = str(contact["Phone_Number"])

    return result


def map_workday_position(wd_record: dict) -> dict:
    """Map Workday position data to Transpop format."""
    return {
        "title": resolve_wid_reference(wd_record.get("Job_Title")) or "",
        "department": resolve_wid_reference(wd_record.get("Department")) or "",
        "location": resolve_wid_reference(wd_record.get("Location")) or "",
        "worker_id": wd_record.get("Worker_Reference", {}).get("WID", ""),
    }


def map_workday_schedule(wd_record: dict) -> dict:
    """Map Workday schedule data to Transpop shift format."""
    name = resolve_wid_reference(wd_record.get("Schedule_Name")) or ""
    return {
        "name": WORKDAY_SCHEDULE_MAP.get(name, name),
        "code": name,
        "worker_id": wd_record.get("Worker_Reference", {}).get("WID", ""),
    }
