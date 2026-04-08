from __future__ import annotations

import logging
import math

logger = logging.getLogger(__name__)

# Average vehicle speed in km/h for urban routes (Morocco)
DEFAULT_SPEED_KMH = 25.0


def haversine_distance_km(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in km
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_eta_seconds(
    vehicle_lat: float,
    vehicle_lng: float,
    stop_lat: float,
    stop_lng: float,
    vehicle_speed_kmh: float | None = None,
) -> int:
    """
    Calculate ETA in seconds from vehicle to stop.
    Uses current vehicle speed if available, otherwise default urban speed.
    """
    distance_km = haversine_distance_km(
        vehicle_lat, vehicle_lng, stop_lat, stop_lng
    )

    speed = vehicle_speed_kmh if vehicle_speed_kmh and vehicle_speed_kmh > 0 else DEFAULT_SPEED_KMH

    # Time = Distance / Speed, convert hours to seconds
    eta_hours = distance_km / speed
    eta_seconds = int(eta_hours * 3600)

    return max(0, eta_seconds)
