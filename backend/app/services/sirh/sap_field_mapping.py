"""SAP SuccessFactors field mapping to Transpop Employee model.

Maps SAP OData entity fields to the internal Employee model fields.
Handles SAP-specific data formats: dates (/Date(timestamp)/), enums, nested objects.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# SAP SuccessFactors → Transpop Employee field mapping
SAP_FIELD_MAP: dict[str, str] = {
    "userId": "matricule",
    "firstName": "first_name",
    "lastName": "last_name",
    "email": "email",
    "department": "department",
    "phoneNumber": "phone",
    "division": "department",
    "businessUnit": "department",
    "customString1": "shift_time",
    "jobTitle": "job_title",
    "hireDate": "hire_date",
    "lastModifiedDateTime": "modified_at",
}

# SAP department code → Transpop department name
SAP_DEPARTMENT_MAP: dict[str, str] = {
    "DEP001": "Production",
    "DEP002": "Logistique",
    "DEP003": "Maintenance",
    "DEP004": "Administration",
    "DEP005": "Ressources Humaines",
    "DEP006": "Informatique",
    "DEP007": "Qualité",
    "DEP008": "Sécurité",
}

# SAP shift codes → Transpop shift labels
SAP_SHIFT_MAP: dict[str, str] = {
    "SHIFT_A": "Équipe Matin",
    "SHIFT_B": "Équipe Après-midi",
    "SHIFT_C": "Équipe Nuit",
    "SHIFT_N": "Normal",
}


def parse_sap_date(value: str | None) -> str | None:
    """Parse SAP OData date format /Date(timestamp)/ to ISO 8601."""
    if not value:
        return None

    # Handle /Date(1234567890000)/ format
    match = re.match(r"/Date\((\d+)\)/", str(value))
    if match:
        timestamp_ms = int(match.group(1))
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        return dt.isoformat()

    # Handle ISO format directly
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        logger.warning("Could not parse SAP date: %s", value)
        return None


def map_sap_employee(sap_record: dict) -> dict:
    """Map a SAP SuccessFactors employee record to Transpop format.

    Args:
        sap_record: Raw record from SAP OData API

    Returns:
        Dict with Transpop Employee field names
    """
    result: dict = {}

    for sap_field, transpop_field in SAP_FIELD_MAP.items():
        value = sap_record.get(sap_field)
        if value is None:
            continue

        # Apply field-specific transformations
        if sap_field in ("hireDate", "lastModifiedDateTime"):
            result[transpop_field] = parse_sap_date(value)
        elif sap_field == "department" and value in SAP_DEPARTMENT_MAP:
            result[transpop_field] = SAP_DEPARTMENT_MAP[value]
        elif sap_field == "customString1" and value in SAP_SHIFT_MAP:
            result[transpop_field] = SAP_SHIFT_MAP[value]
        else:
            result[transpop_field] = str(value)

    # Handle nested address object
    address = sap_record.get("addressInfo") or sap_record.get("homeAddress")
    if isinstance(address, dict):
        result["address"] = _format_address(address)

    # Handle nested employment info
    employment = sap_record.get("employmentInfo") or sap_record.get("empInfo")
    if isinstance(employment, dict):
        if "siteCode" in employment:
            result["site_code"] = employment["siteCode"]
        if "isActive" in employment:
            result["is_active"] = employment["isActive"]

    return result


def _format_address(address: dict) -> str:
    """Format SAP address object to a single address string."""
    parts = []
    for field in ("addressLine1", "addressLine2", "city", "zipCode", "country"):
        val = address.get(field)
        if val:
            parts.append(str(val))
    return ", ".join(parts)


def map_sap_site(sap_record: dict) -> dict:
    """Map SAP location/company record to Transpop site fields."""
    return {
        "code": sap_record.get("locationCode") or sap_record.get("companyCode", ""),
        "name": sap_record.get("locationName") or sap_record.get("companyName", ""),
        "city": sap_record.get("city", ""),
        "address": _format_address(sap_record) if "addressLine1" in sap_record else "",
    }
