"""Route Deviation Detection — compare vehicle position to planned route.

Detects when a vehicle deviates from its planned route by calculating
the perpendicular distance to the nearest route segment and emitting
alerts when the distance exceeds a configurable threshold.

Session 121 — CDC SOTREG v5.0 Module M8.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DEFAULT_DEVIATION_THRESHOLD_M = 200.0  # 200 meters


@dataclass
class RouteSegment:
    """A segment of a planned route."""

    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float


@dataclass
class DeviationResult:
    """Result of a route deviation check."""

    vehicle_id: str
    deviation_m: float
    is_deviated: bool
    threshold_m: float
    nearest_segment_index: int
    planned_route_id: str


def haversine_distance(
    lat1: float, lng1: float, lat2: float, lng2: float,
) -> float:
    """Calculate distance between two points in meters."""
    R = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def point_to_segment_distance(
    lat: float, lng: float,
    seg_start_lat: float, seg_start_lng: float,
    seg_end_lat: float, seg_end_lng: float,
) -> float:
    """Calculate perpendicular distance from point to line segment.

    Uses flat-Earth approximation for short distances (valid for
    segments < 10 km).

    Args:
        lat, lng: Point coordinates.
        seg_start_lat, seg_start_lng: Segment start.
        seg_end_lat, seg_end_lng: Segment end.

    Returns:
        Distance in meters to nearest point on segment.
    """
    # Convert to flat-Earth coordinates (meters)
    cos_lat = math.cos(math.radians(lat))
    M_PER_DEG_LAT = 111_320.0
    M_PER_DEG_LNG = 111_320.0 * cos_lat

    px = (lng - seg_start_lng) * M_PER_DEG_LNG
    py = (lat - seg_start_lat) * M_PER_DEG_LAT

    sx = (seg_end_lng - seg_start_lng) * M_PER_DEG_LNG
    sy = (seg_end_lat - seg_start_lat) * M_PER_DEG_LAT

    seg_len_sq = sx * sx + sy * sy

    if seg_len_sq < 1e-10:
        # Degenerate segment (start == end)
        return math.sqrt(px * px + py * py)

    # Project point onto segment line, clamped to [0, 1]
    t = max(0.0, min(1.0, (px * sx + py * sy) / seg_len_sq))

    # Nearest point on segment
    nearest_x = t * sx
    nearest_y = t * sy

    dx = px - nearest_x
    dy = py - nearest_y
    return math.sqrt(dx * dx + dy * dy)


def check_route_deviation(
    vehicle_id: str,
    lat: float,
    lng: float,
    route_points: list[tuple[float, float]],
    planned_route_id: str = "",
    threshold_m: float = DEFAULT_DEVIATION_THRESHOLD_M,
) -> DeviationResult:
    """Check if a vehicle has deviated from its planned route.

    Calculates the minimum perpendicular distance from the vehicle
    position to any segment of the planned route.

    Args:
        vehicle_id: Vehicle identifier.
        lat: Current vehicle latitude.
        lng: Current vehicle longitude.
        route_points: Ordered list of (lat, lng) route waypoints.
        planned_route_id: ID of the planned route.
        threshold_m: Deviation threshold in meters (default 200).

    Returns:
        DeviationResult with distance, status, and nearest segment.
    """
    if len(route_points) < 2:
        return DeviationResult(
            vehicle_id=vehicle_id,
            deviation_m=0.0,
            is_deviated=False,
            threshold_m=threshold_m,
            nearest_segment_index=0,
            planned_route_id=planned_route_id,
        )

    min_distance = float("inf")
    nearest_idx = 0

    for i in range(len(route_points) - 1):
        s_lat, s_lng = route_points[i]
        e_lat, e_lng = route_points[i + 1]

        dist = point_to_segment_distance(lat, lng, s_lat, s_lng, e_lat, e_lng)
        if dist < min_distance:
            min_distance = dist
            nearest_idx = i

    is_deviated = min_distance > threshold_m

    if is_deviated:
        logger.info(
            "Route deviation: vehicle=%s deviation=%.0fm (threshold=%.0fm)",
            vehicle_id, min_distance, threshold_m,
        )

    return DeviationResult(
        vehicle_id=vehicle_id,
        deviation_m=round(min_distance, 1),
        is_deviated=is_deviated,
        threshold_m=threshold_m,
        nearest_segment_index=nearest_idx,
        planned_route_id=planned_route_id,
    )
