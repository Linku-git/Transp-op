"""Position Interpolation — smooth GPS animation between updates.

Provides linear interpolation, bearing calculation, and speed-based
extrapolation for real-time vehicle tracking visualization.

Session 121 — CDC SOTREG v5.0 Module M8.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeoPosition:
    """A geographic position with metadata."""

    lat: float
    lng: float
    speed_kmh: float = 0.0
    heading: float = 0.0  # degrees 0-360
    timestamp: float = 0.0  # unix epoch seconds


def haversine_distance(
    lat1: float, lng1: float, lat2: float, lng2: float,
) -> float:
    """Calculate haversine distance between two points in meters.

    Args:
        lat1, lng1: First point coordinates (degrees).
        lat2, lng2: Second point coordinates (degrees).

    Returns:
        Distance in meters.
    """
    R = 6_371_000  # Earth radius in meters
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


def calculate_bearing(
    lat1: float, lng1: float, lat2: float, lng2: float,
) -> float:
    """Calculate initial bearing from point 1 to point 2.

    Args:
        lat1, lng1: Start point (degrees).
        lat2, lng2: End point (degrees).

    Returns:
        Bearing in degrees (0-360, 0=North, 90=East).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlam = math.radians(lng2 - lng1)

    x = math.sin(dlam) * math.cos(phi2)
    y = (
        math.cos(phi1) * math.sin(phi2)
        - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    )
    theta = math.atan2(x, y)
    return (math.degrees(theta) + 360) % 360


def interpolate_position(
    start: GeoPosition,
    end: GeoPosition,
    fraction: float,
) -> GeoPosition:
    """Linear interpolation between two GPS positions.

    Args:
        start: Starting position.
        end: Ending position.
        fraction: Interpolation fraction [0.0, 1.0].

    Returns:
        Interpolated GeoPosition.
    """
    fraction = max(0.0, min(1.0, fraction))

    lat = start.lat + (end.lat - start.lat) * fraction
    lng = start.lng + (end.lng - start.lng) * fraction
    speed = start.speed_kmh + (end.speed_kmh - start.speed_kmh) * fraction
    heading = calculate_bearing(start.lat, start.lng, end.lat, end.lng)
    ts = start.timestamp + (end.timestamp - start.timestamp) * fraction

    return GeoPosition(
        lat=lat, lng=lng, speed_kmh=speed, heading=heading, timestamp=ts,
    )


def extrapolate_position(
    position: GeoPosition,
    elapsed_seconds: float,
) -> GeoPosition:
    """Extrapolate position based on current speed and heading.

    Used when GPS updates are delayed to provide estimated position.

    Args:
        position: Last known position with speed and heading.
        elapsed_seconds: Time since last position in seconds.

    Returns:
        Estimated GeoPosition.
    """
    if position.speed_kmh <= 0 or elapsed_seconds <= 0:
        return GeoPosition(
            lat=position.lat, lng=position.lng,
            speed_kmh=position.speed_kmh,
            heading=position.heading,
            timestamp=position.timestamp + elapsed_seconds,
        )

    # Convert speed to m/s and compute distance
    speed_ms = position.speed_kmh / 3.6
    distance_m = speed_ms * elapsed_seconds

    # Convert heading to radians
    bearing_rad = math.radians(position.heading)

    # Approximate displacement (flat Earth for short distances)
    R = 6_371_000
    dlat = (distance_m * math.cos(bearing_rad)) / R
    dlng = (distance_m * math.sin(bearing_rad)) / (
        R * math.cos(math.radians(position.lat))
    )

    return GeoPosition(
        lat=position.lat + math.degrees(dlat),
        lng=position.lng + math.degrees(dlng),
        speed_kmh=position.speed_kmh,
        heading=position.heading,
        timestamp=position.timestamp + elapsed_seconds,
    )


def generate_interpolated_frames(
    start: GeoPosition,
    end: GeoPosition,
    fps: int = 30,
) -> list[GeoPosition]:
    """Generate interpolated frames between two positions.

    Args:
        start: Starting position.
        end: Ending position.
        fps: Frames per second for animation.

    Returns:
        List of interpolated GeoPositions.
    """
    duration = end.timestamp - start.timestamp
    if duration <= 0:
        return [end]

    num_frames = max(1, int(duration * fps))
    frames: list[GeoPosition] = []

    for i in range(num_frames + 1):
        fraction = i / num_frames
        frames.append(interpolate_position(start, end, fraction))

    return frames
