from __future__ import annotations

import logging
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
# Moroccan market pricing (MAD)
# ---------------------------------------------------------------------------

CHARGER_HARDWARE_COSTS_MAD: dict[str, Decimal] = {
    "ac_7kw": Decimal("25000"),
    "ac_22kw": Decimal("45000"),
    "dc_50kw": Decimal("180000"),
    "dc_150kw": Decimal("450000"),
}

INSTALLATION_COST_PER_CHARGER_MAD: dict[str, Decimal] = {
    "ac_7kw": Decimal("8000"),
    "ac_22kw": Decimal("12000"),
    "dc_50kw": Decimal("35000"),
    "dc_150kw": Decimal("60000"),
}

# Power rating per charger type (kW)
CHARGER_POWER_KW: dict[str, int] = {
    "ac_7kw": 7,
    "ac_22kw": 22,
    "dc_50kw": 50,
    "dc_150kw": 150,
}

# Electrical upgrade thresholds
ELECTRICAL_UPGRADE_COST_MAD: Decimal = Decimal("50000")   # per 100kW above 50kW
TRANSFORMER_COST_MAD: Decimal = Decimal("150000")         # if total > 100kW
GRID_CONNECTION_BASE_MAD: Decimal = Decimal("20000")
GRID_CONNECTION_PER_KW_MAD: Decimal = Decimal("500")
CIVIL_WORKS_PER_CHARGER_MAD: Decimal = Decimal("15000")   # trenching, cabling, foundations

VALID_CHARGER_TYPES: list[str] = list(CHARGER_HARDWARE_COSTS_MAD.keys())


# ---------------------------------------------------------------------------
# Depot electrification cost calculator
# ---------------------------------------------------------------------------


def compute_depot_electrification_cost(
    charger_count: int,
    charger_type: str = "dc_50kw",
    contingency_pct: float = 10.0,
    currency: str = "MAD",
) -> dict:
    """Compute total depot electrification cost with 7-component breakdown.

    Components:

    1. **charger_hardware**: unit_cost x count
    2. **installation**: install_cost x count
    3. **electrical_upgrade**: 50,000 MAD per 100 kW above the 50 kW threshold
    4. **transformer**: 150,000 MAD if total installed power > 100 kW, else 0
    5. **grid_connection**: 20,000 MAD base + 500 MAD per kW installed
    6. **civil_works**: 15,000 MAD per charger (trenching, cabling, foundations)
    7. **contingency**: ``contingency_pct`` % of subtotal (items 1-6)

    Args:
        charger_count: Number of chargers to install (must be >= 1).
        charger_type: Key identifying the charger model. One of
            ``ac_7kw``, ``ac_22kw``, ``dc_50kw``, ``dc_150kw``.
        contingency_pct: Contingency percentage applied on the subtotal
            (default 10.0). Must be between 0 and 100.
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:

        - ``charger_hardware_mad`` -- total hardware cost
        - ``installation_mad`` -- total installation cost
        - ``electrical_upgrade_mad`` -- electrical upgrade cost
        - ``transformer_mad`` -- transformer cost (0 if not required)
        - ``grid_connection_mad`` -- grid connection fee
        - ``civil_works_mad`` -- civil works cost
        - ``contingency_mad`` -- contingency amount
        - ``subtotal_mad`` -- sum of components 1-6 (before contingency)
        - ``total_cost_mad`` -- subtotal + contingency
        - ``cost_per_charger_mad`` -- total_cost / charger_count
        - ``charger_type`` -- selected charger type key
        - ``charger_count`` -- number of chargers
        - ``total_power_kw`` -- total installed power (charger_count x power)
        - ``contingency_pct`` -- contingency percentage used
        - ``currency`` -- currency code

    Raises:
        ValueError: If *charger_count* < 1, *charger_type* is unknown,
            or *contingency_pct* is outside [0, 100].
    """
    # ---- Input validation ------------------------------------------------
    if charger_count < 1:
        raise ValueError(f"charger_count must be >= 1, got {charger_count}")
    if charger_type not in CHARGER_HARDWARE_COSTS_MAD:
        raise ValueError(
            f"Unknown charger_type '{charger_type}'. "
            f"Valid types: {VALID_CHARGER_TYPES}"
        )
    if not (0.0 <= contingency_pct <= 100.0):
        raise ValueError(
            f"contingency_pct must be between 0 and 100, got {contingency_pct}"
        )

    # ---- Decimal conversion ----------------------------------------------
    count = _to_dec(charger_count)
    unit_hw_cost = CHARGER_HARDWARE_COSTS_MAD[charger_type]
    unit_install_cost = INSTALLATION_COST_PER_CHARGER_MAD[charger_type]
    power_per_charger = _to_dec(CHARGER_POWER_KW[charger_type])
    total_power = _q(count * power_per_charger)

    # ---- Component 1: Charger hardware -----------------------------------
    charger_hardware = _q(count * unit_hw_cost)

    # ---- Component 2: Installation ---------------------------------------
    installation = _q(count * unit_install_cost)

    # ---- Component 3: Electrical upgrade ---------------------------------
    # 50,000 MAD per 100 kW above the 50 kW threshold
    threshold_kw = Decimal("50")
    if total_power > threshold_kw:
        excess_kw = total_power - threshold_kw
        # Number of 100 kW blocks (ceiling)
        blocks = (excess_kw / Decimal("100")).to_integral_value(
            rounding=ROUND_HALF_UP
        )
        # Ensure at least 1 block if there is any excess
        if blocks < Decimal("1") and excess_kw > Decimal("0"):
            blocks = Decimal("1")
        electrical_upgrade = _q(blocks * ELECTRICAL_UPGRADE_COST_MAD)
    else:
        electrical_upgrade = Decimal("0")

    # ---- Component 4: Transformer ----------------------------------------
    transformer = TRANSFORMER_COST_MAD if total_power > Decimal("100") else Decimal("0")

    # ---- Component 5: Grid connection ------------------------------------
    grid_connection = _q(
        GRID_CONNECTION_BASE_MAD + GRID_CONNECTION_PER_KW_MAD * total_power
    )

    # ---- Component 6: Civil works ----------------------------------------
    civil_works = _q(count * CIVIL_WORKS_PER_CHARGER_MAD)

    # ---- Subtotal (components 1-6) ---------------------------------------
    subtotal = _q(
        charger_hardware
        + installation
        + electrical_upgrade
        + transformer
        + grid_connection
        + civil_works
    )

    # ---- Component 7: Contingency ----------------------------------------
    contingency_rate = _to_dec(contingency_pct) / Decimal("100")
    contingency = _q(subtotal * contingency_rate)

    # ---- Total -----------------------------------------------------------
    total_cost = _q(subtotal + contingency)
    cost_per_charger = _q(total_cost / count)

    logger.info(
        "Depot electrification cost: %d x %s (%s kW total), "
        "subtotal=%s %s, contingency=%s %s (%.1f%%), total=%s %s",
        charger_count,
        charger_type,
        total_power,
        subtotal,
        currency,
        contingency,
        currency,
        contingency_pct,
        total_cost,
        currency,
    )

    return {
        "charger_hardware_mad": float(charger_hardware),
        "installation_mad": float(installation),
        "electrical_upgrade_mad": float(electrical_upgrade),
        "transformer_mad": float(transformer),
        "grid_connection_mad": float(grid_connection),
        "civil_works_mad": float(civil_works),
        "contingency_mad": float(contingency),
        "subtotal_mad": float(subtotal),
        "total_cost_mad": float(total_cost),
        "cost_per_charger_mad": float(cost_per_charger),
        "charger_type": charger_type,
        "charger_count": charger_count,
        "total_power_kw": float(total_power),
        "contingency_pct": contingency_pct,
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Multi-type depot cost estimation
# ---------------------------------------------------------------------------


def compute_mixed_depot_cost(
    charger_mix: dict[str, int],
    contingency_pct: float = 10.0,
    currency: str = "MAD",
) -> dict:
    """Compute depot electrification cost for a heterogeneous charger mix.

    Aggregates costs across multiple charger types, sharing common
    infrastructure costs (transformer, grid connection) calculated from
    the combined total power.

    Args:
        charger_mix: Mapping of charger type to count, e.g.
            ``{"ac_22kw": 5, "dc_50kw": 3}``. Each key must be a valid
            charger type and count >= 1.
        contingency_pct: Contingency percentage (0-100, default 10.0).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:

        - ``per_type_breakdown`` -- list of per-type cost dicts
        - ``total_charger_count`` -- sum of all chargers
        - ``total_power_kw`` -- combined installed power
        - ``shared_electrical_upgrade_mad`` -- electrical upgrade cost
        - ``shared_transformer_mad`` -- transformer cost
        - ``shared_grid_connection_mad`` -- grid connection fee
        - ``total_civil_works_mad`` -- civil works across all types
        - ``subtotal_mad`` -- sum before contingency
        - ``contingency_mad`` -- contingency amount
        - ``total_cost_mad`` -- final total
        - ``contingency_pct`` -- contingency percentage used
        - ``currency`` -- currency code

    Raises:
        ValueError: If *charger_mix* is empty, a type is invalid,
            or any count < 1.
    """
    if not charger_mix:
        raise ValueError("charger_mix must contain at least one entry")

    # Validate all types and counts upfront
    for ctype, ccount in charger_mix.items():
        if ctype not in CHARGER_HARDWARE_COSTS_MAD:
            raise ValueError(
                f"Unknown charger_type '{ctype}'. "
                f"Valid types: {VALID_CHARGER_TYPES}"
            )
        if ccount < 1:
            raise ValueError(
                f"Count for '{ctype}' must be >= 1, got {ccount}"
            )
    if not (0.0 <= contingency_pct <= 100.0):
        raise ValueError(
            f"contingency_pct must be between 0 and 100, got {contingency_pct}"
        )

    # ---- Per-type hardware + installation + civil works ------------------
    per_type_breakdown: list[dict] = []
    total_hardware = Decimal("0")
    total_installation = Decimal("0")
    total_civil = Decimal("0")
    total_power = Decimal("0")
    total_count = 0

    for ctype, ccount in charger_mix.items():
        count_d = _to_dec(ccount)
        hw = _q(count_d * CHARGER_HARDWARE_COSTS_MAD[ctype])
        inst = _q(count_d * INSTALLATION_COST_PER_CHARGER_MAD[ctype])
        civil = _q(count_d * CIVIL_WORKS_PER_CHARGER_MAD)
        power = _q(count_d * _to_dec(CHARGER_POWER_KW[ctype]))

        total_hardware += hw
        total_installation += inst
        total_civil += civil
        total_power += power
        total_count += ccount

        per_type_breakdown.append({
            "charger_type": ctype,
            "count": ccount,
            "power_kw": float(power),
            "hardware_mad": float(hw),
            "installation_mad": float(inst),
            "civil_works_mad": float(civil),
        })

    total_power = _q(total_power)

    # ---- Shared infrastructure costs -------------------------------------
    # Electrical upgrade
    threshold_kw = Decimal("50")
    if total_power > threshold_kw:
        excess_kw = total_power - threshold_kw
        blocks = (excess_kw / Decimal("100")).to_integral_value(
            rounding=ROUND_HALF_UP
        )
        if blocks < Decimal("1") and excess_kw > Decimal("0"):
            blocks = Decimal("1")
        electrical_upgrade = _q(blocks * ELECTRICAL_UPGRADE_COST_MAD)
    else:
        electrical_upgrade = Decimal("0")

    # Transformer
    transformer = TRANSFORMER_COST_MAD if total_power > Decimal("100") else Decimal("0")

    # Grid connection
    grid_connection = _q(
        GRID_CONNECTION_BASE_MAD + GRID_CONNECTION_PER_KW_MAD * total_power
    )

    # ---- Subtotal --------------------------------------------------------
    subtotal = _q(
        total_hardware
        + total_installation
        + electrical_upgrade
        + transformer
        + grid_connection
        + total_civil
    )

    # ---- Contingency -----------------------------------------------------
    contingency_rate = _to_dec(contingency_pct) / Decimal("100")
    contingency = _q(subtotal * contingency_rate)

    total_cost = _q(subtotal + contingency)

    logger.info(
        "Mixed depot cost: %d chargers (%s kW total), "
        "subtotal=%s %s, total=%s %s",
        total_count,
        total_power,
        subtotal,
        currency,
        total_cost,
        currency,
    )

    return {
        "per_type_breakdown": per_type_breakdown,
        "total_charger_count": total_count,
        "total_power_kw": float(total_power),
        "shared_electrical_upgrade_mad": float(electrical_upgrade),
        "shared_transformer_mad": float(transformer),
        "shared_grid_connection_mad": float(grid_connection),
        "total_civil_works_mad": float(_q(total_civil)),
        "subtotal_mad": float(subtotal),
        "contingency_mad": float(contingency),
        "total_cost_mad": float(total_cost),
        "contingency_pct": contingency_pct,
        "currency": currency,
    }
