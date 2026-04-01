from __future__ import annotations

import logging
from dataclasses import dataclass, field

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
# Table service (distance/time matrix)
# ---------------------------------------------------------------------------


@dataclass
class TableResult:
    """Result from OSRM table service."""

    durations: list[list[float]]  # seconds, NxN matrix
    distances: list[list[float]]  # meters, NxN matrix


async def osrm_table(
    coordinates: list[tuple[float, float]],
    profile: str = "driving",
) -> TableResult:
    """Get a distance/duration matrix for multiple coordinates.

    Args:
        coordinates: List of (lat, lng) tuples.
        profile: OSRM profile ('driving', 'walking', 'cycling').

    Returns:
        TableResult with NxN duration and distance matrices.
    """
    if len(coordinates) < 2:
        return TableResult(durations=[[0.0]], distances=[[0.0]])

    coords_str = ";".join(f"{lng},{lat}" for lat, lng in coordinates)
    url = f"{settings.osrm_url}/table/v1/{profile}/{coords_str}"
    params = {"annotations": "duration,distance"}

    try:
        async with httpx.AsyncClient(timeout=OSRM_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok":
            logger.warning("OSRM table failed: %s", data.get("message", "unknown"))
            return _haversine_table_fallback(coordinates)

        durations = data.get("durations", [])
        distances = data.get("distances", [])

        if not durations or not distances:
            logger.warning("OSRM table returned empty matrices")
            return _haversine_table_fallback(coordinates)

        return TableResult(durations=durations, distances=distances)

    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.warning("OSRM table request failed: %s", exc)
        return _haversine_table_fallback(coordinates)


def _haversine_table_fallback(
    coordinates: list[tuple[float, float]],
) -> TableResult:
    """Build a distance/duration matrix using haversine when OSRM is unavailable.

    Duration is estimated assuming a driving speed of 40 km/h.
    """
    n = len(coordinates)
    driving_speed_ms = 40_000.0 / 3600.0  # 40 km/h in m/s

    durations: list[list[float]] = []
    distances: list[list[float]] = []

    for i in range(n):
        dur_row: list[float] = []
        dist_row: list[float] = []
        for j in range(n):
            if i == j:
                dur_row.append(0.0)
                dist_row.append(0.0)
            else:
                d = _haversine_meters(
                    coordinates[i][0], coordinates[i][1],
                    coordinates[j][0], coordinates[j][1],
                )
                dist_row.append(d)
                dur_row.append(d / driving_speed_ms)
        durations.append(dur_row)
        distances.append(dist_row)

    return TableResult(durations=durations, distances=distances)


# ---------------------------------------------------------------------------
# Multi-waypoint route service
# ---------------------------------------------------------------------------


@dataclass
class RouteLeg:
    """A single leg between consecutive waypoints."""

    distance_meters: float
    duration_seconds: float


@dataclass
class MultiRouteResult:
    """Result from OSRM route service with multiple waypoints."""

    distance_meters: float
    duration_seconds: float
    geometry: str | None = None  # encoded polyline
    legs: list[RouteLeg] = field(default_factory=list)


async def osrm_route_multi(
    waypoints: list[tuple[float, float]],
    profile: str = "driving",
) -> MultiRouteResult:
    """Get a route through multiple waypoints in order.

    Args:
        waypoints: List of (lat, lng) tuples in visit order.
        profile: OSRM profile ('driving', 'walking', 'cycling').

    Returns:
        MultiRouteResult with total distance, duration, geometry, and per-leg details.
    """
    if len(waypoints) < 2:
        return MultiRouteResult(distance_meters=0.0, duration_seconds=0.0)

    coords_str = ";".join(f"{lng},{lat}" for lat, lng in waypoints)
    url = f"{settings.osrm_url}/route/v1/{profile}/{coords_str}"
    params = {"overview": "full", "geometries": "polyline", "steps": "false"}

    try:
        async with httpx.AsyncClient(timeout=OSRM_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            logger.warning("OSRM route_multi failed: %s", data.get("message", "unknown"))
            return _haversine_multi_fallback(waypoints)

        route = data["routes"][0]
        legs: list[RouteLeg] = []
        for leg_data in route.get("legs", []):
            legs.append(
                RouteLeg(
                    distance_meters=leg_data["distance"],
                    duration_seconds=leg_data["duration"],
                )
            )

        return MultiRouteResult(
            distance_meters=route["distance"],
            duration_seconds=route["duration"],
            geometry=route.get("geometry"),
            legs=legs,
        )

    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.warning("OSRM route_multi request failed: %s", exc)
        return _haversine_multi_fallback(waypoints)


def _haversine_multi_fallback(
    waypoints: list[tuple[float, float]],
) -> MultiRouteResult:
    """Build a multi-waypoint route result using haversine when OSRM is unavailable."""
    driving_speed_ms = 40_000.0 / 3600.0  # 40 km/h in m/s
    total_dist = 0.0
    total_dur = 0.0
    legs: list[RouteLeg] = []

    for i in range(len(waypoints) - 1):
        d = _haversine_meters(
            waypoints[i][0], waypoints[i][1],
            waypoints[i + 1][0], waypoints[i + 1][1],
        )
        dur = d / driving_speed_ms
        legs.append(RouteLeg(distance_meters=d, duration_seconds=dur))
        total_dist += d
        total_dur += dur

    return MultiRouteResult(
        distance_meters=total_dist,
        duration_seconds=total_dur,
        legs=legs,
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
