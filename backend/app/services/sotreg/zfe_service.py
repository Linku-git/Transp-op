from __future__ import annotations

import asyncio
import logging
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ligne import Ligne

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ADEME ZFE API configuration
# ---------------------------------------------------------------------------
_ADEME_ZFE_URL = (
    "https://data.ademe.fr/data-fair/api/v1/datasets/zfe/lines"
)
_ADEME_TIMEOUT = 10.0
_USER_AGENT = "Transpop/0.1 (transport-optimization)"

# ---------------------------------------------------------------------------
# Local ZFE registry (Moroccan context — configurable fallback)
# ---------------------------------------------------------------------------
_LOCAL_ZFE_ZONES: list[dict] = [
    {
        "name": "Casablanca Centre",
        "center_lat": 33.5731,
        "center_lng": -7.5898,
        "radius_km": 5.0,
        "restriction_level": "moderate",
        "allowed_crit_air": [1, 2, 3],
    },
    {
        "name": "Rabat Agdal",
        "center_lat": 33.9911,
        "center_lng": -6.8498,
        "radius_km": 3.0,
        "restriction_level": "low",
        "allowed_crit_air": [1, 2, 3, 4],
    },
    {
        "name": "Tanger Medina",
        "center_lat": 35.7595,
        "center_lng": -5.8340,
        "radius_km": 2.5,
        "restriction_level": "moderate",
        "allowed_crit_air": [1, 2, 3],
    },
]


# ---------------------------------------------------------------------------
# ZFE result dataclass
# ---------------------------------------------------------------------------
@dataclass
class ZFEResult:
    """Result of a ZFE compliance check for a single point."""

    is_in_zfe: bool
    zone_name: str | None = None
    restriction_level: str | None = None
    allowed_crit_air: list[int] | None = field(default=None)
    checked_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Haversine distance (local implementation)
# ---------------------------------------------------------------------------
def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance in km between two points."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _is_in_france(lat: float, lng: float) -> bool:
    """Rough bounding-box check for metropolitan France."""
    return 41.0 <= lat <= 51.5 and -5.5 <= lng <= 9.5


def _check_local_registry(lat: float, lng: float) -> ZFEResult:
    """Check coordinates against the local ZFE zone registry."""
    for zone in _LOCAL_ZFE_ZONES:
        dist = _haversine_km(lat, lng, zone["center_lat"], zone["center_lng"])
        if dist < zone["radius_km"]:
            logger.debug(
                "Point (%.4f, %.4f) is inside local ZFE '%s' (dist=%.2f km)",
                lat,
                lng,
                zone["name"],
                dist,
            )
            return ZFEResult(
                is_in_zfe=True,
                zone_name=zone["name"],
                restriction_level=zone["restriction_level"],
                allowed_crit_air=list(zone["allowed_crit_air"]),
            )

    return ZFEResult(is_in_zfe=False)


async def _check_ademe_api(lat: float, lng: float) -> ZFEResult | None:
    """Query the ADEME ZFE API for a point in France.

    Returns a ``ZFEResult`` if the API responds successfully, or ``None``
    if the API is unreachable or returns an error so that the caller can
    fall back to the local registry.
    """
    # Build a small bounding box around the point (~500m)
    delta = 0.005
    bbox = f"{lng - delta},{lat - delta},{lng + delta},{lat + delta}"

    try:
        async with httpx.AsyncClient(timeout=_ADEME_TIMEOUT) as client:
            response = await client.get(
                _ADEME_ZFE_URL,
                params={"bbox": bbox, "size": 1},
                headers={"User-Agent": _USER_AGENT},
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            if not results:
                return ZFEResult(is_in_zfe=False)

            hit = results[0]
            zone_name = hit.get("nom") or hit.get("name")
            restriction = hit.get("vignettes_interdites") or hit.get(
                "restriction_level", "unknown"
            )
            allowed_raw = hit.get("vignettes_autorisees", "")
            allowed_crit: list[int] | None = None
            if isinstance(allowed_raw, str) and allowed_raw:
                try:
                    allowed_crit = [int(x.strip()) for x in allowed_raw.split(",") if x.strip()]
                except ValueError:
                    allowed_crit = None

            logger.info(
                "ADEME ZFE hit for (%.4f, %.4f): zone=%s restriction=%s",
                lat,
                lng,
                zone_name,
                restriction,
            )
            return ZFEResult(
                is_in_zfe=True,
                zone_name=zone_name,
                restriction_level=str(restriction) if restriction else None,
                allowed_crit_air=allowed_crit,
            )

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "ADEME ZFE API HTTP error for (%.4f, %.4f): %s %s",
            lat,
            lng,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except (httpx.RequestError, ValueError, KeyError) as exc:
        logger.warning(
            "ADEME ZFE API request failed for (%.4f, %.4f): %s",
            lat,
            lng,
            exc,
        )
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def check_zfe_compliance(lat: float, lng: float) -> ZFEResult:
    """Check whether a point is inside a ZFE zone.

    Strategy:
    1. If the point is within France, try the ADEME API first.
    2. If the ADEME API is unreachable or the point is outside France,
       fall back to the configurable local ZFE registry.
    """
    if _is_in_france(lat, lng):
        ademe_result = await _check_ademe_api(lat, lng)
        if ademe_result is not None:
            return ademe_result
        logger.info(
            "ADEME API unavailable; falling back to local registry for "
            "(%.4f, %.4f)",
            lat,
            lng,
        )

    return _check_local_registry(lat, lng)


async def batch_check_zfe(
    coordinates: list[tuple[float, float]],
) -> list[ZFEResult]:
    """Check multiple coordinates for ZFE compliance concurrently.

    Args:
        coordinates: List of ``(lat, lng)`` tuples.

    Returns:
        List of ``ZFEResult`` in the same order as the input coordinates.
    """
    if not coordinates:
        return []

    tasks = [check_zfe_compliance(lat, lng) for lat, lng in coordinates]
    results: list[ZFEResult] = await asyncio.gather(*tasks)
    logger.info(
        "Batch ZFE check: %d coordinates, %d in ZFE",
        len(coordinates),
        sum(1 for r in results if r.is_in_zfe),
    )
    return results


async def check_ligne_zfe_compliance(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[dict]:
    """Check all active lignes for ZFE compliance on both origin and dest.

    Returns a list of dicts with ligne info and ZFE status for each endpoint.
    """
    stmt = select(Ligne).where(
        Ligne.tenant_id == tenant_id,
        Ligne.is_active.is_(True),
    )
    result = await db.execute(stmt)
    lignes = result.scalars().all()

    if not lignes:
        logger.info("No active lignes found for tenant %s", tenant_id)
        return []

    # Collect all coordinates for batch check
    origin_coords: list[tuple[float, float]] = []
    dest_coords: list[tuple[float, float]] = []
    for ligne in lignes:
        origin_coords.append((ligne.origin_lat, ligne.origin_lng))
        dest_coords.append((ligne.dest_lat, ligne.dest_lng))

    origin_results, dest_results = await asyncio.gather(
        batch_check_zfe(origin_coords),
        batch_check_zfe(dest_coords),
    )

    compliance_list: list[dict] = []
    for i, ligne in enumerate(lignes):
        origin_zfe = origin_results[i]
        dest_zfe = dest_results[i]

        compliance_list.append(
            {
                "ligne_id": str(ligne.id),
                "ligne_code": ligne.code,
                "ligne_name": ligne.name,
                "origin": {
                    "lat": ligne.origin_lat,
                    "lng": ligne.origin_lng,
                    "is_in_zfe": origin_zfe.is_in_zfe,
                    "zone_name": origin_zfe.zone_name,
                    "restriction_level": origin_zfe.restriction_level,
                    "allowed_crit_air": origin_zfe.allowed_crit_air,
                },
                "dest": {
                    "lat": ligne.dest_lat,
                    "lng": ligne.dest_lng,
                    "is_in_zfe": dest_zfe.is_in_zfe,
                    "zone_name": dest_zfe.zone_name,
                    "restriction_level": dest_zfe.restriction_level,
                    "allowed_crit_air": dest_zfe.allowed_crit_air,
                },
                "any_endpoint_in_zfe": origin_zfe.is_in_zfe or dest_zfe.is_in_zfe,
                "checked_at": origin_zfe.checked_at.isoformat(),
            }
        )

    in_zfe_count = sum(1 for c in compliance_list if c["any_endpoint_in_zfe"])
    logger.info(
        "Ligne ZFE compliance: %d/%d lignes have at least one endpoint in a ZFE",
        in_zfe_count,
        len(compliance_list),
    )
    return compliance_list
