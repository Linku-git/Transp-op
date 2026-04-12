"""Geofence Detection — PostGIS ST_DWithin-based enter/exit events.

Detects when vehicles enter or exit defined geofence zones (polygon
or circle), tracking state transitions and emitting alerts.

Session 121 — CDC SOTREG v5.0 Module M8.
"""
from __future__ import annotations

import logging
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GeofenceType(str, Enum):
    """Geofence geometry type."""

    CIRCLE = "circle"
    POLYGON = "polygon"


class AlertType(str, Enum):
    """Geofence alert type."""

    ENTER = "enter"
    EXIT = "exit"


@dataclass
class Geofence:
    """A geofence zone definition."""

    id: str
    name: str
    fence_type: GeofenceType
    center_lat: float = 0.0
    center_lng: float = 0.0
    radius_m: float = 0.0  # for circle type
    polygon: list[tuple[float, float]] = field(default_factory=list)  # for polygon type
    active: bool = True


@dataclass
class GeofenceAlert:
    """Alert emitted on geofence state transition."""

    vehicle_id: str
    geofence_id: str
    geofence_name: str
    alert_type: AlertType
    lat: float
    lng: float
    timestamp: float


class GeofenceDetector:
    """Stateful geofence detector tracking per-vehicle inside/outside state.

    Uses haversine distance for circle geofences and ray-casting
    for polygon geofences. In production, PostGIS ST_DWithin and
    ST_Contains would replace the in-memory calculations.
    """

    def __init__(self, geofences: list[Geofence] | None = None) -> None:
        self._geofences: dict[str, Geofence] = {}
        self._vehicle_state: dict[str, set[str]] = {}  # vehicle_id -> set of geofence_ids inside

        if geofences:
            for gf in geofences:
                self._geofences[gf.id] = gf

    def add_geofence(self, geofence: Geofence) -> None:
        """Register a geofence zone."""
        self._geofences[geofence.id] = geofence

    def remove_geofence(self, geofence_id: str) -> None:
        """Remove a geofence zone."""
        self._geofences.pop(geofence_id, None)

    @property
    def geofence_count(self) -> int:
        """Number of active geofences."""
        return sum(1 for gf in self._geofences.values() if gf.active)

    def check_position(
        self,
        vehicle_id: str,
        lat: float,
        lng: float,
        timestamp: float = 0.0,
    ) -> list[GeofenceAlert]:
        """Check vehicle position against all active geofences.

        Detects enter/exit transitions by comparing current state
        with previous state for this vehicle.

        Args:
            vehicle_id: Vehicle identifier.
            lat: Current latitude.
            lng: Current longitude.
            timestamp: Position timestamp (unix epoch).

        Returns:
            List of GeofenceAlert objects for state transitions.
        """
        alerts: list[GeofenceAlert] = []
        prev_inside = self._vehicle_state.get(vehicle_id, set())
        curr_inside: set[str] = set()

        for gf_id, gf in self._geofences.items():
            if not gf.active:
                continue

            inside = self._is_inside(gf, lat, lng)
            if inside:
                curr_inside.add(gf_id)

        # Detect transitions
        entered = curr_inside - prev_inside
        exited = prev_inside - curr_inside

        for gf_id in entered:
            gf = self._geofences[gf_id]
            alerts.append(GeofenceAlert(
                vehicle_id=vehicle_id,
                geofence_id=gf_id,
                geofence_name=gf.name,
                alert_type=AlertType.ENTER,
                lat=lat, lng=lng, timestamp=timestamp,
            ))
            logger.info("Geofence ENTER: vehicle=%s fence=%s", vehicle_id, gf.name)

        for gf_id in exited:
            gf = self._geofences[gf_id]
            alerts.append(GeofenceAlert(
                vehicle_id=vehicle_id,
                geofence_id=gf_id,
                geofence_name=gf.name,
                alert_type=AlertType.EXIT,
                lat=lat, lng=lng, timestamp=timestamp,
            ))
            logger.info("Geofence EXIT: vehicle=%s fence=%s", vehicle_id, gf.name)

        self._vehicle_state[vehicle_id] = curr_inside
        return alerts

    def get_vehicle_state(self, vehicle_id: str) -> set[str]:
        """Get current geofence membership for a vehicle."""
        return self._vehicle_state.get(vehicle_id, set())

    def _is_inside(self, geofence: Geofence, lat: float, lng: float) -> bool:
        """Check if a point is inside a geofence."""
        if geofence.fence_type == GeofenceType.CIRCLE:
            return self._point_in_circle(
                lat, lng, geofence.center_lat, geofence.center_lng, geofence.radius_m,
            )
        elif geofence.fence_type == GeofenceType.POLYGON:
            return self._point_in_polygon(lat, lng, geofence.polygon)
        return False

    @staticmethod
    def _point_in_circle(
        lat: float, lng: float,
        center_lat: float, center_lng: float,
        radius_m: float,
    ) -> bool:
        """Check if point is within circle (haversine distance)."""
        R = 6_371_000
        phi1 = math.radians(lat)
        phi2 = math.radians(center_lat)
        dphi = math.radians(center_lat - lat)
        dlam = math.radians(center_lng - lng)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance <= radius_m

    @staticmethod
    def _point_in_polygon(
        lat: float, lng: float,
        polygon: list[tuple[float, float]],
    ) -> bool:
        """Ray-casting algorithm for point-in-polygon test."""
        n = len(polygon)
        if n < 3:
            return False

        inside = False
        j = n - 1
        for i in range(n):
            yi, xi = polygon[i]
            yj, xj = polygon[j]
            if ((yi > lng) != (yj > lng)) and (
                lat < (xj - xi) * (lng - yi) / (yj - yi) + xi
            ):
                inside = not inside
            j = i
        return inside
