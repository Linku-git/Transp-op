"""SOTREG demo seed data generator for development.

Generates realistic transport line, stop, telemetry, and AVL metric
data for the Casablanca metropolitan area. All coordinates fall within
the Casablanca bounding box (lat 33.5-33.7, lng -7.3 to -7.7).

Usage::

    from app.db.seed_sotreg import (
        generate_seed_lignes,
        generate_seed_stops,
        generate_seed_telemetry,
        generate_seed_avl_metrics,
        is_seed_loaded,
    )
"""
from __future__ import annotations

import logging
import math
import random
import uuid
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Reproducible seed for consistent demo data
random.seed(42)

# ---------------------------------------------------------------------------
# Casablanca route definitions — realistic origin/destination pairs
# ---------------------------------------------------------------------------

CASABLANCA_ROUTES: list[dict] = [
    {
        "code": "L001",
        "name": "Navette Casa-Port -> Ain Sebaa",
        "origin": (33.5950, -7.6167),
        "dest": (33.6133, -7.5494),
    },
    {
        "code": "L002",
        "name": "Liaison Mohammedia -> Ain Harrouda",
        "origin": (33.6867, -7.3919),
        "dest": (33.6375, -7.4592),
    },
    {
        "code": "L003",
        "name": "Express Hay Hassani -> Zone Indus Nouaceur",
        "origin": (33.5575, -7.6535),
        "dest": (33.4842, -7.5844),
    },
    {
        "code": "L004",
        "name": "Navette Sidi Bernoussi -> Mediouna",
        "origin": (33.6265, -7.5211),
        "dest": (33.5120, -7.5140),
    },
    {
        "code": "L005",
        "name": "Liaison Maarif -> Bouskoura ZI",
        "origin": (33.5792, -7.6313),
        "dest": (33.4900, -7.6466),
    },
    {
        "code": "L006",
        "name": "Navette Bernoussi -> Tit Mellil",
        "origin": (33.6289, -7.5237),
        "dest": (33.5890, -7.4830),
    },
    {
        "code": "L007",
        "name": "Express Anfa -> Casa Nearshore",
        "origin": (33.5977, -7.6443),
        "dest": (33.5556, -7.6615),
    },
    {
        "code": "L008",
        "name": "Liaison Hay Mohammadi -> Sidi Maarouf",
        "origin": (33.5857, -7.5551),
        "dest": (33.5440, -7.6390),
    },
    {
        "code": "L009",
        "name": "Navette Ain Chock -> Lissasfa",
        "origin": (33.5505, -7.5752),
        "dest": (33.5250, -7.6100),
    },
    {
        "code": "L010",
        "name": "Express Oulfa -> Aeroport Med V",
        "origin": (33.5614, -7.5658),
        "dest": (33.5030, -7.5890),
    },
    {
        "code": "L011",
        "name": "Liaison Ben M'Sick -> Moulay Rachid",
        "origin": (33.5614, -7.5658),
        "dest": (33.5472, -7.5844),
    },
    {
        "code": "L012",
        "name": "Navette Sidi Othmane -> Ain Sebaa Nord",
        "origin": (33.5552, -7.5605),
        "dest": (33.6203, -7.5318),
    },
    {
        "code": "L013",
        "name": "Express CIL -> Zone Franche Tanger Med",
        "origin": (33.5688, -7.6257),
        "dest": (33.6050, -7.4950),
    },
    {
        "code": "L014",
        "name": "Liaison Bourgogne -> Zenata",
        "origin": (33.5836, -7.6183),
        "dest": (33.6650, -7.4450),
    },
    {
        "code": "L015",
        "name": "Navette Belvedere -> Sidi Moumen",
        "origin": (33.5975, -7.5750),
        "dest": (33.5850, -7.5200),
    },
    {
        "code": "L016",
        "name": "Express Racine -> Dar Bouazza",
        "origin": (33.5833, -7.6438),
        "dest": (33.5150, -7.7050),
    },
    {
        "code": "L017",
        "name": "Liaison Oasis -> El Jadida Gate",
        "origin": (33.5598, -7.6385),
        "dest": (33.5320, -7.6850),
    },
    {
        "code": "L018",
        "name": "Navette Val Fleuri -> Roches Noires",
        "origin": (33.5850, -7.5625),
        "dest": (33.6070, -7.5730),
    },
    {
        "code": "L019",
        "name": "Express California -> Bouskoura Golf",
        "origin": (33.5782, -7.6413),
        "dest": (33.4950, -7.6280),
    },
    {
        "code": "L020",
        "name": "Liaison El Fida -> Ain Sebaa Sud",
        "origin": (33.5826, -7.5876),
        "dest": (33.6133, -7.5400),
    },
]

# ---------------------------------------------------------------------------
# Configuration pools for diversity
# ---------------------------------------------------------------------------

MOTORIZATION_TYPES: list[str] = ["diesel", "electric", "hybrid", "gnc"]
MOTORIZATION_WEIGHTS: list[float] = [0.50, 0.20, 0.20, 0.10]

VEHICLE_TYPES: list[str] = [
    "bus_standard",
    "bus_articule",
    "minibus",
    "midibus",
    "van_12places",
]

SERVICE_TYPES: list[str] = ["navette", "express", "liaison", "intersite"]
SERVICE_WEIGHTS: list[float] = [0.35, 0.25, 0.25, 0.15]

SHIFT_TYPES: list[str] = [
    "matin_06h",
    "matin_07h",
    "journee_08h",
    "aprem_14h",
    "nuit_22h",
]

# Casablanca neighborhoods for stop placement
STOP_NEIGHBORHOODS: list[tuple[str, float, float]] = [
    ("Ain Chock", 33.5505, -7.5752),
    ("Ain Sebaa", 33.6203, -7.5318),
    ("Anfa", 33.5977, -7.6443),
    ("Belvedere", 33.5975, -7.5750),
    ("Bernoussi", 33.6289, -7.5237),
    ("Bourgogne", 33.5836, -7.6183),
    ("California", 33.5782, -7.6413),
    ("El Fida", 33.5826, -7.5876),
    ("Habous", 33.5718, -7.6099),
    ("Hay Hassani", 33.5575, -7.6535),
    ("Hay Mohammadi", 33.5857, -7.5551),
    ("Maarif", 33.5792, -7.6313),
    ("Sidi Belyout", 33.5917, -7.6059),
    ("Sidi Bernoussi", 33.6265, -7.5211),
    ("CIL", 33.5688, -7.6257),
    ("Oasis", 33.5598, -7.6385),
    ("Racine", 33.5833, -7.6438),
    ("Val Fleuri", 33.5850, -7.5625),
    ("Ben M'Sick", 33.5614, -7.5658),
    ("Sidi Othmane", 33.5552, -7.5605),
    ("Moulay Rachid", 33.5472, -7.5844),
    ("Sbata", 33.5400, -7.5750),
    ("Lissasfa", 33.5250, -7.6100),
    ("Nouaceur", 33.4842, -7.5844),
    ("Bouskoura", 33.4900, -7.6466),
    ("Dar Bouazza", 33.5150, -7.7050),
    ("Sidi Maarouf", 33.5440, -7.6390),
    ("Roches Noires", 33.6070, -7.5730),
    ("Mediouna", 33.5120, -7.5140),
    ("Tit Mellil", 33.5890, -7.4830),
]

# AVL metric types matching the AVLMetric model
AVL_METRIC_TYPES: list[str] = [
    "otp",           # On-Time Performance (%)
    "headway_cov",   # Headway coefficient of variation
    "load_factor",   # Average load factor (%)
    "avg_speed",     # Average speed (km/h)
]

# Target ranges for realistic KPI generation
AVL_TARGETS: dict[str, dict] = {
    "otp": {"mean": 85.0, "std": 8.0, "min": 50.0, "max": 100.0, "target": 90.0},
    "headway_cov": {"mean": 0.25, "std": 0.10, "min": 0.05, "max": 0.80, "target": 0.20},
    "load_factor": {"mean": 65.0, "std": 15.0, "min": 15.0, "max": 100.0, "target": 75.0},
    "avg_speed": {"mean": 28.0, "std": 8.0, "min": 8.0, "max": 55.0, "target": 30.0},
}


# ---------------------------------------------------------------------------
# Haversine distance helper
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return great-circle distance in km between two points."""
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
# Seed generators
# ---------------------------------------------------------------------------


def generate_seed_lignes(
    tenant_id: str,
    count: int = 20,
) -> list[dict]:
    """Generate transport lines with realistic Casablanca coordinates.

    Each line gets a realistic distance computed via haversine, diverse
    motorization/service types, and the CDC formula components
    (D x R x J = km_annual).

    Args:
        tenant_id: Tenant UUID string.
        count: Number of lines to generate (max 20 from route definitions).

    Returns:
        List of dicts matching the ``Ligne`` model columns.
    """
    count = min(count, len(CASABLANCA_ROUTES))
    lignes: list[dict] = []

    for i, route in enumerate(CASABLANCA_ROUTES[:count]):
        origin_lat, origin_lng = route["origin"]
        dest_lat, dest_lng = route["dest"]

        # Compute realistic distance (haversine * 1.3 road factor)
        straight_km = _haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
        road_km = round(straight_km * 1.3, 1)
        road_km = max(road_km, 3.0)  # minimum 3 km route

        # CDC formula components
        rotations = random.choice([2, 3, 4, 5, 6])
        operating_days = random.choice([250, 260, 280, 300, 312])
        km_annual = round(road_km * rotations * operating_days, 0)

        # Diverse configuration
        motorization = random.choices(
            MOTORIZATION_TYPES, weights=MOTORIZATION_WEIGHTS, k=1
        )[0]
        service_type = random.choices(
            SERVICE_TYPES, weights=SERVICE_WEIGHTS, k=1
        )[0]
        vehicle_type = random.choice(VEHICLE_TYPES)
        shift_type = random.choice(SHIFT_TYPES)
        passenger_count = random.randint(15, 55)

        # Terrain: Casablanca is mostly flat with some moderate slopes
        pente = round(random.uniform(0.5, 4.0), 1)

        ligne = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "code": route["code"],
            "name": route["name"],
            "site_id": None,
            "origin_lat": origin_lat,
            "origin_lng": origin_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "distance_km": road_km,
            "rotations_per_day": rotations,
            "operating_days_per_year": operating_days,
            "km_annual": km_annual,
            "vehicle_type": vehicle_type,
            "motorization": motorization,
            "passenger_count_avg": passenger_count,
            "shift_type": shift_type,
            "service_type": service_type,
            "pente_moyenne_pct": pente,
            "is_active": True,
        }
        lignes.append(ligne)

    logger.info(
        "Generated %d seed lignes for tenant %s (total km_annual=%.0f)",
        len(lignes),
        tenant_id,
        sum(l["km_annual"] for l in lignes),
    )
    return lignes


def generate_seed_stops(
    tenant_id: str,
    count: int = 50,
) -> list[dict]:
    """Generate transit stops along Casablanca corridors.

    Stops are placed near known neighborhoods with small random offsets
    to simulate real stop locations. Each stop includes a capacity,
    shelter presence, and PMR accessibility flag.

    Args:
        tenant_id: Tenant UUID string.
        count: Number of stops to generate (draws from 30 neighborhoods).

    Returns:
        List of stop dicts suitable for insertion into a stops table.
    """
    stops: list[dict] = []
    neighborhoods = STOP_NEIGHBORHOODS.copy()

    for i in range(count):
        # Cycle through neighborhoods, adding small offsets for variety
        base = neighborhoods[i % len(neighborhoods)]
        name_base = base[0]
        base_lat = base[1]
        base_lng = base[2]

        # Random offset: ~50-300 meters
        lat_offset = random.uniform(-0.003, 0.003)
        lng_offset = random.uniform(-0.003, 0.003)

        lat = round(base_lat + lat_offset, 6)
        lng = round(base_lng + lng_offset, 6)

        # Generate unique stop name with suffix for duplicates
        suffix_idx = i // len(neighborhoods)
        stop_name = (
            f"Arret {name_base}"
            if suffix_idx == 0
            else f"Arret {name_base} {suffix_idx + 1}"
        )

        capacity = random.choice([10, 15, 20, 25, 30, 40, 50])
        has_shelter = random.random() < 0.6
        is_pmr_accessible = random.random() < 0.4

        stop = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "code": f"S{i + 1:03d}",
            "name": stop_name,
            "lat": lat,
            "lng": lng,
            "capacity": capacity,
            "has_shelter": has_shelter,
            "is_pmr_accessible": is_pmr_accessible,
            "neighborhood": name_base,
            "is_active": True,
        }
        stops.append(stop)

    logger.info(
        "Generated %d seed stops for tenant %s across %d neighborhoods",
        len(stops),
        tenant_id,
        len(set(s["neighborhood"] for s in stops)),
    )
    return stops


def generate_seed_telemetry(
    tenant_id: str,
    vehicle_ids: list[str],
    days: int = 7,
) -> list[dict]:
    """Generate sample telemetry readings for a set of vehicles.

    Produces GPS position, speed, fuel/battery level, and engine status
    readings at 5-minute intervals during operating hours (06:00-22:00).

    Args:
        tenant_id: Tenant UUID string.
        vehicle_ids: List of vehicle UUID strings.
        days: Number of past days to generate data for (default 7).

    Returns:
        List of telemetry reading dicts.
    """
    readings: list[dict] = []
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    for vehicle_id in vehicle_ids:
        # Assign a random base location in Casablanca
        base_lat = random.uniform(33.50, 33.65)
        base_lng = random.uniform(-7.70, -7.45)

        for day_offset in range(days):
            current_day = start_date + timedelta(days=day_offset)

            # Operating hours: 06:00 to 22:00, readings every 5 minutes
            # Generate ~48 readings per day (4 hours sampled, not all 16)
            num_readings = random.randint(30, 60)
            for _ in range(num_readings):
                hour = random.randint(6, 21)
                minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                timestamp = current_day.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )

                # Simulate movement around base location
                lat = round(base_lat + random.uniform(-0.02, 0.02), 6)
                lng = round(base_lng + random.uniform(-0.02, 0.02), 6)
                speed_kmh = round(random.gauss(25, 12), 1)
                speed_kmh = max(0.0, min(80.0, speed_kmh))

                # Fuel/battery level declines through the day
                base_level = 95.0 - (hour - 6) * 3.5
                fuel_level = round(
                    max(10.0, base_level + random.uniform(-5, 5)), 1
                )

                odometer_km = round(random.uniform(50000, 350000), 1)

                reading = {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "vehicle_id": vehicle_id,
                    "timestamp": timestamp.isoformat(),
                    "lat": lat,
                    "lng": lng,
                    "speed_kmh": speed_kmh,
                    "heading_deg": round(random.uniform(0, 360), 1),
                    "fuel_or_battery_pct": fuel_level,
                    "odometer_km": odometer_km,
                    "engine_on": speed_kmh > 0,
                    "ignition_on": True,
                }
                readings.append(reading)

    logger.info(
        "Generated %d telemetry readings for %d vehicles over %d days "
        "(tenant %s)",
        len(readings),
        len(vehicle_ids),
        days,
        tenant_id,
    )
    return readings


def generate_seed_avl_metrics(
    tenant_id: str,
    ligne_ids: list[str],
    days: int = 30,
) -> list[dict]:
    """Generate daily AVL KPI metrics for transport lines.

    Produces OTP, headway COV, load factor, and average speed metrics
    with realistic distributions and weekday/weekend patterns. Values
    are compared against targets to set the ``meets_target`` flag.

    Args:
        tenant_id: Tenant UUID string.
        ligne_ids: List of ligne UUID strings.
        days: Number of past days to generate metrics for (default 30).

    Returns:
        List of dicts matching ``AVLMetric`` model columns.
    """
    metrics: list[dict] = []
    now = datetime.now(timezone.utc)

    for ligne_id in ligne_ids:
        # Each line has a baseline performance profile
        line_bias = {
            "otp": random.uniform(-5, 5),
            "headway_cov": random.uniform(-0.05, 0.05),
            "load_factor": random.uniform(-10, 10),
            "avg_speed": random.uniform(-5, 5),
        }

        for day_offset in range(days):
            metric_date = (now - timedelta(days=days - day_offset)).date()
            weekday = metric_date.weekday()

            # Skip Sundays (most Moroccan industrial sites closed)
            if weekday == 6:
                continue

            # Saturday has reduced service
            is_saturday = weekday == 5

            for metric_type in AVL_METRIC_TYPES:
                target_cfg = AVL_TARGETS[metric_type]
                mean = target_cfg["mean"] + line_bias[metric_type]

                # Weekend adjustment: slightly worse performance
                if is_saturday:
                    if metric_type == "otp":
                        mean -= 3.0
                    elif metric_type == "load_factor":
                        mean -= 15.0
                    elif metric_type == "avg_speed":
                        mean += 3.0  # less congestion

                value = random.gauss(mean, target_cfg["std"])
                value = max(target_cfg["min"], min(target_cfg["max"], value))
                value = round(value, 2)

                # Determine if target is met
                target = target_cfg["target"]
                if metric_type == "headway_cov":
                    meets_target = value <= target  # lower is better
                else:
                    meets_target = value >= target  # higher is better

                sample_size = random.randint(8, 40) if not is_saturday else random.randint(4, 15)

                metric = {
                    "id": str(uuid.uuid4()),
                    "tenant_id": tenant_id,
                    "ligne_id": ligne_id,
                    "vehicle_id": None,
                    "metric_type": metric_type,
                    "value": value,
                    "metric_date": metric_date.isoformat(),
                    "period": "daily",
                    "sample_size": sample_size,
                    "meets_target": meets_target,
                    "details": None,
                }
                metrics.append(metric)

    logger.info(
        "Generated %d AVL metrics for %d lignes over %d days (tenant %s)",
        len(metrics),
        len(ligne_ids),
        days,
        tenant_id,
    )
    return metrics


# ---------------------------------------------------------------------------
# Idempotency check
# ---------------------------------------------------------------------------

# In-memory marker to avoid re-running in the same process.  For a
# database-level check, callers should query for existing Ligne records
# with a known SOTREG code prefix.
_SEED_MARKER: dict[str, bool] = {}


def is_seed_loaded(tenant_id: str) -> bool:
    """Check if SOTREG seed data has already been generated for a tenant.

    This performs an in-memory check only. For persistent idempotency,
    the caller should query the ``ligne`` table for records with code
    starting with ``L0`` for the given tenant.

    Args:
        tenant_id: Tenant UUID string.

    Returns:
        ``True`` if seed data was already generated in this process.
    """
    return _SEED_MARKER.get(tenant_id, False)


def mark_seed_loaded(tenant_id: str) -> None:
    """Mark SOTREG seed data as loaded for a tenant (in-memory).

    Args:
        tenant_id: Tenant UUID string.
    """
    _SEED_MARKER[tenant_id] = True
    logger.info("SOTREG seed data marked as loaded for tenant %s", tenant_id)
