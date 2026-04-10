from __future__ import annotations

import logging
import math
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_dec(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# Layout parameters (meters)
# ---------------------------------------------------------------------------

CHARGER_BAY_WIDTH_M: float = 3.5        # width per charger bay
CHARGER_BAY_DEPTH_M: float = 7.0        # depth per charger bay (vehicle + clearance)
CHARGER_SPACING_M: float = 1.5          # minimum space between chargers
SAFETY_ZONE_M: float = 2.0              # clearance around charger area
PARKING_BAY_AREA_M2: float = 15.0       # per standard parking bay
MAINTENANCE_AREA_MIN_M2: float = 50.0   # minimum maintenance area
MAINTENANCE_AREA_PER_VEHICLE_M2: float = 5.0  # additional per fleet vehicle
CIRCULATION_FACTOR: float = 1.3         # 30% added for driveways and access

# Charger power lookup (for labelling; consistent with charging_optimizer)
CHARGER_POWER_KW: dict[str, int] = {
    "ac_7kw": 7,
    "ac_22kw": 22,
    "dc_50kw": 50,
    "dc_150kw": 150,
}

VALID_CHARGER_TYPES: list[str] = list(CHARGER_POWER_KW.keys())


# ---------------------------------------------------------------------------
# Charger position generator
# ---------------------------------------------------------------------------


def _generate_charger_positions(
    charger_count: int,
    bay_width: float,
    bay_depth: float,
    spacing: float,
    safety_zone: float,
) -> list[dict[str, float]]:
    """Generate (x, y) centre coordinates for each charger bay.

    Chargers are arranged in a single row along the X axis, offset from the
    origin by the safety zone. Each bay is separated by the minimum spacing.

    Args:
        charger_count: Number of charger bays to place (>= 0).
        bay_width: Width of each bay in metres.
        bay_depth: Depth of each bay in metres.
        spacing: Minimum horizontal spacing between bays in metres.
        safety_zone: Clearance offset from the area edge in metres.

    Returns:
        List of dicts, each with ``x``, ``y``, ``bay_width``, ``bay_depth``.
    """
    if charger_count <= 0:
        return []

    positions: list[dict[str, float]] = []
    for i in range(charger_count):
        x = safety_zone + i * (bay_width + spacing) + bay_width / 2.0
        y = safety_zone + bay_depth / 2.0
        positions.append({
            "x": round(x, 2),
            "y": round(y, 2),
            "bay_width": bay_width,
            "bay_depth": bay_depth,
        })

    return positions


# ---------------------------------------------------------------------------
# Charging area computation
# ---------------------------------------------------------------------------


def _compute_charging_area(
    charger_count: int,
    bay_width: float,
    bay_depth: float,
    spacing: float,
    safety_zone: float,
) -> tuple[float, float, float]:
    """Compute charging area dimensions and total area.

    The charging zone is a rectangle that contains all charger bays plus
    safety clearance on all sides.

    Args:
        charger_count: Number of charger bays (>= 0).
        bay_width: Width of each bay in metres.
        bay_depth: Depth of each bay in metres.
        spacing: Horizontal spacing between bays in metres.
        safety_zone: Clearance on all sides in metres.

    Returns:
        Tuple of ``(area_m2, total_width_m, total_depth_m)``.
    """
    if charger_count <= 0:
        return 0.0, 0.0, 0.0

    # Width: N bays + (N-1) spacings + safety on both sides
    inner_width = charger_count * bay_width + (charger_count - 1) * spacing
    total_width = inner_width + 2.0 * safety_zone

    # Depth: one bay deep + safety on both sides
    total_depth = bay_depth + 2.0 * safety_zone

    area = total_width * total_depth
    return round(area, 2), round(total_width, 2), round(total_depth, 2)


# ---------------------------------------------------------------------------
# Depot layout planner
# ---------------------------------------------------------------------------


def compute_depot_layout(
    charger_count: int,
    fleet_size: int,
    charger_type: str = "dc_50kw",
    include_maintenance: bool = True,
    currency: str = "MAD",
) -> dict:
    """Plan depot layout for N chargers and M vehicles.

    Computes the spatial requirements for a depot that accommodates the
    specified charging infrastructure and fleet parking. All measurements
    are in metres and square metres.

    Areas computed:

    - **charging_area_m2**: Charger bays arranged in a single row, plus
      inter-bay spacing (1.5 m) and safety clearance (2.0 m) on all sides.
    - **parking_area_m2**: ``fleet_size`` x 15.0 m2 per standard bay.
    - **maintenance_area_m2**: 50.0 m2 base + 5.0 m2 per fleet vehicle
      (or 0 if *include_maintenance* is ``False``).
    - **circulation_area_m2**: 30% of the sum of the above for driveways,
      turning radii, and access roads.
    - **total_area_m2**: Sum of all area components.

    Charger positions are reported as a list of ``(x, y)`` centre
    coordinates suitable for rendering on a depot map.

    Edge cases:

    - Zero chargers: charging area is 0; positions list is empty.
    - Zero fleet: parking area is 0; maintenance scales to minimum only.
    - Single vehicle: minimum viable layout returned.

    Args:
        charger_count: Number of chargers to install (must be >= 0).
        fleet_size: Number of vehicles in the fleet (must be >= 0).
        charger_type: Key identifying the charger model. One of
            ``ac_7kw``, ``ac_22kw``, ``dc_50kw``, ``dc_150kw``.
        include_maintenance: Whether to include a maintenance area
            in the layout (default ``True``).
        currency: Currency code for labelling (default ``"MAD"``).

    Returns:
        Dict containing:

        - ``total_area_m2`` -- total depot footprint
        - ``charging_area_m2`` -- area for charger bays + clearances
        - ``parking_area_m2`` -- area for fleet parking
        - ``maintenance_area_m2`` -- area for maintenance (0 if excluded)
        - ``circulation_area_m2`` -- driveways and access roads
        - ``charger_positions`` -- list of ``{x, y, bay_width, bay_depth}``
        - ``parking_bays`` -- number of parking bays (= fleet_size)
        - ``charger_count`` -- number of chargers
        - ``charger_type`` -- selected charger type key
        - ``charger_power_kw`` -- power per charger
        - ``total_power_kw`` -- total installed power
        - ``dimensions`` -- ``{width_m, depth_m}`` estimated rectangular
          footprint of the full depot
        - ``include_maintenance`` -- whether maintenance area was included
        - ``currency`` -- currency code

    Raises:
        ValueError: If *charger_count* < 0, *fleet_size* < 0,
            or *charger_type* is unknown.
    """
    # ---- Input validation ------------------------------------------------
    if charger_count < 0:
        raise ValueError(
            f"charger_count must be >= 0, got {charger_count}"
        )
    if fleet_size < 0:
        raise ValueError(f"fleet_size must be >= 0, got {fleet_size}")
    if charger_type not in CHARGER_POWER_KW:
        raise ValueError(
            f"Unknown charger_type '{charger_type}'. "
            f"Valid types: {VALID_CHARGER_TYPES}"
        )

    power_per_charger = CHARGER_POWER_KW[charger_type]
    total_power = charger_count * power_per_charger

    # ---- Charging area ---------------------------------------------------
    charging_area, charging_width, charging_depth = _compute_charging_area(
        charger_count=charger_count,
        bay_width=CHARGER_BAY_WIDTH_M,
        bay_depth=CHARGER_BAY_DEPTH_M,
        spacing=CHARGER_SPACING_M,
        safety_zone=SAFETY_ZONE_M,
    )

    # ---- Charger positions -----------------------------------------------
    charger_positions = _generate_charger_positions(
        charger_count=charger_count,
        bay_width=CHARGER_BAY_WIDTH_M,
        bay_depth=CHARGER_BAY_DEPTH_M,
        spacing=CHARGER_SPACING_M,
        safety_zone=SAFETY_ZONE_M,
    )

    # ---- Parking area ----------------------------------------------------
    parking_area = round(fleet_size * PARKING_BAY_AREA_M2, 2)

    # ---- Maintenance area ------------------------------------------------
    if include_maintenance and (charger_count > 0 or fleet_size > 0):
        maintenance_area = round(
            MAINTENANCE_AREA_MIN_M2
            + fleet_size * MAINTENANCE_AREA_PER_VEHICLE_M2,
            2,
        )
    else:
        maintenance_area = 0.0

    # ---- Circulation area (30% of functional areas) ----------------------
    functional_sum = charging_area + parking_area + maintenance_area
    circulation_area = round(
        functional_sum * (CIRCULATION_FACTOR - 1.0), 2
    )

    # ---- Total area ------------------------------------------------------
    total_area = round(
        functional_sum + circulation_area, 2
    )

    # ---- Estimated rectangular footprint ---------------------------------
    # Assume a roughly 2:1 width-to-depth ratio for the full depot.
    # If total area > 0, derive dimensions; otherwise 0x0.
    if total_area > 0:
        estimated_width = round(math.sqrt(total_area * 2.0), 2)
        estimated_depth = round(total_area / estimated_width, 2) if estimated_width > 0 else 0.0
    else:
        estimated_width = 0.0
        estimated_depth = 0.0

    logger.info(
        "Depot layout: %d chargers (%s, %d kW total), %d parking bays, "
        "total_area=%.1f m2 (charging=%.1f, parking=%.1f, "
        "maintenance=%.1f, circulation=%.1f), "
        "footprint=%.1f x %.1f m",
        charger_count,
        charger_type,
        total_power,
        fleet_size,
        total_area,
        charging_area,
        parking_area,
        maintenance_area,
        circulation_area,
        estimated_width,
        estimated_depth,
    )

    return {
        "total_area_m2": total_area,
        "charging_area_m2": charging_area,
        "parking_area_m2": parking_area,
        "maintenance_area_m2": maintenance_area,
        "circulation_area_m2": circulation_area,
        "charger_positions": charger_positions,
        "parking_bays": fleet_size,
        "charger_count": charger_count,
        "charger_type": charger_type,
        "charger_power_kw": power_per_charger,
        "total_power_kw": total_power,
        "dimensions": {
            "width_m": estimated_width,
            "depth_m": estimated_depth,
        },
        "include_maintenance": include_maintenance,
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Multi-zone depot layout
# ---------------------------------------------------------------------------


def compute_multi_zone_layout(
    charger_mix: dict[str, int],
    fleet_size: int,
    include_maintenance: bool = True,
    currency: str = "MAD",
) -> dict:
    """Plan depot layout with separate charging zones per charger type.

    Each charger type gets its own zone with independent bay layout and
    safety clearances. Parking, maintenance, and circulation areas are
    shared across all zones.

    Args:
        charger_mix: Mapping of charger type to count, e.g.
            ``{"ac_22kw": 5, "dc_50kw": 3}``. Each key must be a valid
            charger type and count >= 0.
        fleet_size: Number of vehicles in the fleet (>= 0).
        include_maintenance: Whether to include a maintenance area.
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:

        - ``zones`` -- list of per-type zone dicts with area, positions,
          and dimensions
        - ``total_charging_area_m2`` -- combined charging zone area
        - ``parking_area_m2`` -- fleet parking area
        - ``maintenance_area_m2`` -- maintenance area
        - ``circulation_area_m2`` -- driveways and access
        - ``total_area_m2`` -- full depot footprint
        - ``total_charger_count`` -- sum of all chargers
        - ``total_power_kw`` -- combined installed power
        - ``parking_bays`` -- number of parking bays
        - ``dimensions`` -- ``{width_m, depth_m}`` estimated footprint
        - ``currency`` -- currency code

    Raises:
        ValueError: If *charger_mix* is empty, a type is invalid,
            any count < 0, or *fleet_size* < 0.
    """
    if not charger_mix:
        raise ValueError("charger_mix must contain at least one entry")
    if fleet_size < 0:
        raise ValueError(f"fleet_size must be >= 0, got {fleet_size}")

    for ctype, ccount in charger_mix.items():
        if ctype not in CHARGER_POWER_KW:
            raise ValueError(
                f"Unknown charger_type '{ctype}'. "
                f"Valid types: {VALID_CHARGER_TYPES}"
            )
        if ccount < 0:
            raise ValueError(
                f"Count for '{ctype}' must be >= 0, got {ccount}"
            )

    # ---- Per-zone computation --------------------------------------------
    zones: list[dict] = []
    total_charging_area = 0.0
    total_charger_count = 0
    total_power = 0

    for ctype, ccount in charger_mix.items():
        area, zone_width, zone_depth = _compute_charging_area(
            charger_count=ccount,
            bay_width=CHARGER_BAY_WIDTH_M,
            bay_depth=CHARGER_BAY_DEPTH_M,
            spacing=CHARGER_SPACING_M,
            safety_zone=SAFETY_ZONE_M,
        )

        positions = _generate_charger_positions(
            charger_count=ccount,
            bay_width=CHARGER_BAY_WIDTH_M,
            bay_depth=CHARGER_BAY_DEPTH_M,
            spacing=CHARGER_SPACING_M,
            safety_zone=SAFETY_ZONE_M,
        )

        power_kw = CHARGER_POWER_KW[ctype]
        zone_power = ccount * power_kw

        zones.append({
            "charger_type": ctype,
            "charger_count": ccount,
            "power_per_charger_kw": power_kw,
            "zone_power_kw": zone_power,
            "area_m2": area,
            "dimensions": {
                "width_m": zone_width,
                "depth_m": zone_depth,
            },
            "charger_positions": positions,
        })

        total_charging_area += area
        total_charger_count += ccount
        total_power += zone_power

    total_charging_area = round(total_charging_area, 2)

    # ---- Shared areas ----------------------------------------------------
    parking_area = round(fleet_size * PARKING_BAY_AREA_M2, 2)

    if include_maintenance and (total_charger_count > 0 or fleet_size > 0):
        maintenance_area = round(
            MAINTENANCE_AREA_MIN_M2
            + fleet_size * MAINTENANCE_AREA_PER_VEHICLE_M2,
            2,
        )
    else:
        maintenance_area = 0.0

    functional_sum = total_charging_area + parking_area + maintenance_area
    circulation_area = round(
        functional_sum * (CIRCULATION_FACTOR - 1.0), 2
    )
    total_area = round(functional_sum + circulation_area, 2)

    # ---- Estimated footprint ---------------------------------------------
    if total_area > 0:
        estimated_width = round(math.sqrt(total_area * 2.0), 2)
        estimated_depth = round(total_area / estimated_width, 2) if estimated_width > 0 else 0.0
    else:
        estimated_width = 0.0
        estimated_depth = 0.0

    logger.info(
        "Multi-zone depot layout: %d chargers across %d zones "
        "(%d kW total), total_area=%.1f m2",
        total_charger_count,
        len(zones),
        total_power,
        total_area,
    )

    return {
        "zones": zones,
        "total_charging_area_m2": total_charging_area,
        "parking_area_m2": parking_area,
        "maintenance_area_m2": maintenance_area,
        "circulation_area_m2": circulation_area,
        "total_area_m2": total_area,
        "total_charger_count": total_charger_count,
        "total_power_kw": total_power,
        "parking_bays": fleet_size,
        "dimensions": {
            "width_m": estimated_width,
            "depth_m": estimated_depth,
        },
        "include_maintenance": include_maintenance,
        "currency": currency,
    }
