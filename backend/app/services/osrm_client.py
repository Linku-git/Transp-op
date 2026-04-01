from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OSRM_TIMEOUT = 10.0


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class NearestResult:
    """Result from OSRM nearest service."""

    lat: float
    lng: float
    distance_meters: float
    road_name: str | None = None


@dataclass
class RouteResult:
    """Result from OSRM route service."""

    distance_meters: float
    duration_seconds: float
    geometry: str | None = None  # Encoded polyline


# ---------------------------------------------------------------------------
# OSRM API calls
# ---------------------------------------------------------------------------


async def osrm_nearest(
    lat: float,
    lng: float,
    profile: str = "driving",
) -> NearestResult:
    """Find the nearest point on the road network.

    Args:
        lat: Latitude of the query point.
        lng: Longitude of the query point.
        profile: OSRM profile ('driving', 'walking', 'cycling').

    Returns:
        NearestResult with snapped coordinates and distance.
    """
    url = f"{settings.osrm_url}/nearest/v1/{profile}/{lng},{lat}"
    params = {"number": 1}

    async with httpx.AsyncClient(timeout=OSRM_TIMEOUT) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok" or not data.get("waypoints"):
        logger.warning("OSRM nearest failed for (%f, %f): %s", lat, lng, data)
        # Fallback: return original point
        return NearestResult(lat=lat, lng=lng, distance_meters=0.0)

    waypoint = data["waypoints"][0]
    snapped_lng, snapped_lat = waypoint["location"]
    snap_distance = waypoint.get("distance", 0.0)
    road_name = waypoint.get("name", None)

    return NearestResult(
        lat=snapped_lat,
        lng=snapped_lng,
        distance_meters=snap_distance,
        road_name=road_name,
    )


async def osrm_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    profile: str = "walking",
) -> RouteResult:
    """Get a route between two points.

    Args:
        origin_lat, origin_lng: Origin coordinates.
        dest_lat, dest_lng: Destination coordinates.
        profile: OSRM profile ('driving', 'walking', 'cycling').

    Returns:
        RouteResult with distance, duration, and geometry.
    """
    coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
    url = f"{settings.osrm_url}/route/v1/{profile}/{coords}"
    params = {"overview": "simplified", "geometries": "polyline"}

    async with httpx.AsyncClient(timeout=OSRM_TIMEOUT) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        logger.warning(
            "OSRM route failed for (%f,%f)->(%f,%f): %s",
            origin_lat, origin_lng, dest_lat, dest_lng, data,
        )
        # Fallback: estimate using haversine
        dist = _haversine_meters(origin_lat, origin_lng, dest_lat, dest_lng)
        walking_speed = 4.5  # km/h
        duration = (dist / 1000.0) / walking_speed * 3600.0
        return RouteResult(
            distance_meters=dist,
            duration_seconds=duration,
        )

    route = data["routes"][0]
    return RouteResult(
        distance_meters=route["distance"],
        duration_seconds=route["duration"],
        geometry=route.get("geometry"),
    )


# ---------------------------------------------------------------------------
# Haversine fallback
# ---------------------------------------------------------------------------

import math


def _haversine_meters(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    """Haversine distance in meters between two lat/lng points."""
    R = 6_371_000.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
