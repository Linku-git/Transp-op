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
# ONEE (Morocco) electricity tariff structure
# ---------------------------------------------------------------------------

ONEE_TARIFF_MAD_KWH: dict[str, Decimal] = {
    "pointe": Decimal("1.58"),       # Peak: 17h-22h
    "pleine": Decimal("1.22"),       # Full: 07h-17h
    "creuse": Decimal("0.82"),       # Off-peak: 22h-07h
}

ONEE_DEMAND_CHARGE_MAD_KVA: Decimal = Decimal("200.0")  # Monthly demand charge per kVA

# Blended average tariff (weighted by typical depot usage pattern:
# ~60% creuse, ~30% pleine, ~10% pointe)
ONEE_BLENDED_TARIFF_MAD_KWH: Decimal = _q(
    Decimal("0.60") * ONEE_TARIFF_MAD_KWH["creuse"]
    + Decimal("0.30") * ONEE_TARIFF_MAD_KWH["pleine"]
    + Decimal("0.10") * ONEE_TARIFF_MAD_KWH["pointe"]
)

TOU_WINDOWS: list[dict[str, str | int]] = [
    {"name": "creuse",  "start": 22, "end": 7,  "tariff_key": "creuse"},
    {"name": "pleine",  "start": 7,  "end": 17, "tariff_key": "pleine"},
    {"name": "pointe",  "start": 17, "end": 22, "tariff_key": "pointe"},
]

# ---------------------------------------------------------------------------
# IRVE charger specifications
# ---------------------------------------------------------------------------

CHARGER_SPECS: dict[str, dict[str, int | str]] = {
    "ac_7kw": {
        "power_kw": 7,
        "type": "AC",
        "cost_mad": 25000,
        "install_cost_mad": 8000,
    },
    "ac_22kw": {
        "power_kw": 22,
        "type": "AC",
        "cost_mad": 45000,
        "install_cost_mad": 12000,
    },
    "dc_50kw": {
        "power_kw": 50,
        "type": "DC",
        "cost_mad": 180000,
        "install_cost_mad": 35000,
    },
    "dc_150kw": {
        "power_kw": 150,
        "type": "DC",
        "cost_mad": 450000,
        "install_cost_mad": 60000,
    },
}


# ---------------------------------------------------------------------------
# Time-of-use helpers
# ---------------------------------------------------------------------------


def _hours_in_window(
    window_start: int,
    window_end: int,
    period_start: int,
    period_end: int,
) -> Decimal:
    """Compute overlapping hours between a TOU window and a charging period.

    All hours are in 24h format. Windows may wrap around midnight
    (e.g., creuse 22h-07h).

    Args:
        window_start: TOU window start hour (0-23).
        window_end: TOU window end hour (0-23).
        period_start: Charging period start hour (0-23).
        period_end: Charging period end hour (0-23).

    Returns:
        Decimal hours of overlap (non-negative).
    """

    def _expand(start: int, end: int) -> set[int]:
        """Expand an hour range into a set of individual hours, wrapping midnight."""
        hours: set[int] = set()
        h = start
        while h != end:
            hours.add(h)
            h = (h + 1) % 24
        return hours

    window_hours = _expand(window_start, window_end)
    period_hours = _expand(period_start, period_end)
    overlap = window_hours & period_hours
    return _to_dec(len(overlap))


def _charging_period_duration(arrival_hour: int, departure_hour: int) -> Decimal:
    """Compute total charging period duration in hours.

    Args:
        arrival_hour: Vehicle arrival hour (0-23).
        departure_hour: Vehicle departure hour (0-23).

    Returns:
        Decimal hours available for charging.
    """
    if departure_hour > arrival_hour:
        return _to_dec(departure_hour - arrival_hour)
    # Wraps midnight: e.g., arrival 18h -> departure 6h = 12 hours
    return _to_dec(24 - arrival_hour + departure_hour)


# ---------------------------------------------------------------------------
# Part 1: ChargingOptimizer -- SOC=62% departure target (Qin 2016)
# ---------------------------------------------------------------------------


def compute_charging_schedule(
    battery_capacity_kwh: float,
    current_soc_pct: float,
    target_soc_pct: float = 62.0,
    charger_power_kw: float = 50.0,
    departure_hour: int = 6,
    arrival_hour: int = 18,
    currency: str = "MAD",
) -> dict:
    """Compute optimal charging schedule to reach target SOC by departure.

    Implements the Qin 2016 insight: maintaining SOC at 62% balances battery
    longevity with operational range. The strategy prioritises charging during
    *creuse* (off-peak) hours to minimise electricity costs.

    The algorithm distributes energy demand across TOU windows within the
    available charging period (arrival -> departure), filling cheapest windows
    first (creuse before pleine before pointe).

    Args:
        battery_capacity_kwh: Total battery capacity in kWh (must be > 0).
        current_soc_pct: Current state of charge as percentage (0-100).
        target_soc_pct: Target SOC at departure (default 62.0, Qin 2016
            optimal). Must be >= current_soc_pct.
        charger_power_kw: Charger rated power in kW (must be > 0).
        departure_hour: Hour of day when vehicle departs (0-23).
        arrival_hour: Hour of day when vehicle arrives at depot (0-23).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``target_soc_pct`` -- target SOC percentage
        - ``energy_needed_kwh`` -- total energy to charge
        - ``charging_duration_hours`` -- time required at rated power
        - ``schedule`` -- list of window allocations, each with
          ``window_name``, ``start_hour``, ``end_hour``,
          ``duration_hours``, ``energy_kwh``, ``cost_mad``
        - ``total_energy_cost_mad`` -- sum of window costs
        - ``peak_demand_kw`` -- maximum power draw (for demand charge)
        - ``monthly_demand_charge_mad`` -- peak_demand * ONEE rate
        - ``currency`` -- currency code

    Raises:
        ValueError: If inputs violate physical or business constraints.
    """
    # ---- Input validation ------------------------------------------------
    if battery_capacity_kwh <= 0:
        raise ValueError(
            f"battery_capacity_kwh must be positive, got {battery_capacity_kwh}"
        )
    if not (0.0 <= current_soc_pct <= 100.0):
        raise ValueError(
            f"current_soc_pct must be between 0 and 100, got {current_soc_pct}"
        )
    if not (0.0 <= target_soc_pct <= 100.0):
        raise ValueError(
            f"target_soc_pct must be between 0 and 100, got {target_soc_pct}"
        )
    if charger_power_kw <= 0:
        raise ValueError(
            f"charger_power_kw must be positive, got {charger_power_kw}"
        )
    if not (0 <= departure_hour <= 23):
        raise ValueError(
            f"departure_hour must be between 0 and 23, got {departure_hour}"
        )
    if not (0 <= arrival_hour <= 23):
        raise ValueError(
            f"arrival_hour must be between 0 and 23, got {arrival_hour}"
        )

    capacity = _to_dec(battery_capacity_kwh)
    current_soc = _to_dec(current_soc_pct)
    target_soc = _to_dec(target_soc_pct)
    power = _to_dec(charger_power_kw)

    # ---- Energy computation ----------------------------------------------
    soc_delta = target_soc - current_soc
    if soc_delta < Decimal("0"):
        # Already above target; no charging needed
        logger.info(
            "Current SOC (%.1f%%) >= target SOC (%.1f%%): no charging needed",
            current_soc_pct,
            target_soc_pct,
        )
        return {
            "target_soc_pct": target_soc_pct,
            "energy_needed_kwh": 0.0,
            "charging_duration_hours": 0.0,
            "schedule": [],
            "total_energy_cost_mad": 0.0,
            "peak_demand_kw": 0.0,
            "monthly_demand_charge_mad": 0.0,
            "currency": currency,
        }

    energy_needed = _q(soc_delta / Decimal("100") * capacity)
    charging_duration = _q(energy_needed / power)

    # ---- Available charging period ---------------------------------------
    total_available = _charging_period_duration(arrival_hour, departure_hour)

    if charging_duration > total_available:
        logger.warning(
            "Charging requires %.2f hours but only %.2f hours available "
            "(arrival=%dh, departure=%dh). Will charge at maximum rate for "
            "available duration.",
            float(charging_duration),
            float(total_available),
            arrival_hour,
            departure_hour,
        )

    # ---- Distribute across TOU windows (cheapest first) ------------------
    # Sort windows by tariff (cheapest first for cost optimisation)
    sorted_windows = sorted(
        TOU_WINDOWS,
        key=lambda w: ONEE_TARIFF_MAD_KWH[str(w["tariff_key"])],
    )

    remaining_energy = energy_needed
    schedule: list[dict] = []

    for window in sorted_windows:
        if remaining_energy <= Decimal("0"):
            break

        w_start = int(window["start"])
        w_end = int(window["end"])
        w_name = str(window["name"])
        tariff_key = str(window["tariff_key"])

        # Hours of overlap between this TOU window and the charging period
        overlap_hours = _hours_in_window(
            w_start, w_end, arrival_hour, departure_hour
        )

        if overlap_hours <= Decimal("0"):
            continue

        # Energy that can be delivered in this window at rated power
        max_energy_in_window = _q(overlap_hours * power)
        energy_allocated = min(remaining_energy, max_energy_in_window)
        duration_allocated = _q(energy_allocated / power)

        tariff = ONEE_TARIFF_MAD_KWH[tariff_key]
        cost = _q(energy_allocated * tariff)

        schedule.append({
            "window_name": w_name,
            "start_hour": w_start,
            "end_hour": w_end,
            "duration_hours": float(duration_allocated),
            "energy_kwh": float(energy_allocated),
            "cost_mad": float(cost),
        })

        remaining_energy -= energy_allocated

    # ---- Totals ----------------------------------------------------------
    total_energy_cost = _q(
        sum((_to_dec(s["cost_mad"]) for s in schedule), Decimal("0"))
    )

    # Peak demand is the charger's rated power (assuming constant draw)
    peak_demand_kw = power if energy_needed > Decimal("0") else Decimal("0")
    monthly_demand_charge = _q(peak_demand_kw * ONEE_DEMAND_CHARGE_MAD_KVA)

    logger.info(
        "Charging schedule computed: %.2f kWh over %.2f hours, "
        "cost=%s %s, peak_demand=%s kW, demand_charge=%s %s/month "
        "(SOC %.1f%% -> %.1f%%)",
        float(energy_needed),
        float(charging_duration),
        total_energy_cost,
        currency,
        peak_demand_kw,
        monthly_demand_charge,
        currency,
        current_soc_pct,
        target_soc_pct,
    )

    return {
        "target_soc_pct": target_soc_pct,
        "energy_needed_kwh": float(energy_needed),
        "charging_duration_hours": float(charging_duration),
        "schedule": schedule,
        "total_energy_cost_mad": float(total_energy_cost),
        "peak_demand_kw": float(peak_demand_kw),
        "monthly_demand_charge_mad": float(monthly_demand_charge),
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Part 2: IRVESizingService
# ---------------------------------------------------------------------------


def compute_irve_sizing(
    fleet_size: int,
    daily_km_per_vehicle: float,
    battery_capacity_kwh: float,
    energy_consumption_kwh_per_km: float = 0.25,
    charging_window_hours: float = 8.0,
    charger_utilization_target: float = 0.75,
    preferred_charger_type: str = "dc_50kw",
    currency: str = "MAD",
) -> dict:
    """Compute IRVE (Infrastructure de Recharge pour Vehicules Electriques) sizing.

    Determines the number and type of chargers needed for a fleet, plus the
    full capital and operating cost breakdown.

    Logic:
        1. ``daily_energy_per_vehicle = daily_km * consumption``
        2. ``vehicles_per_charger = (charging_window * charger_power
           / daily_energy) * utilization``
        3. ``charger_count = ceil(fleet_size / vehicles_per_charger)``

    Infrastructure costs include:
        - Hardware: charger unit cost * count
        - Installation: per-charger installation cost
        - Transformer: 150,000 MAD if total installed power > 100 kW
        - Grid connection: 20,000 MAD base + 500 MAD per kW

    Args:
        fleet_size: Number of electric vehicles in the fleet (must be >= 1).
        daily_km_per_vehicle: Average daily distance per vehicle in km
            (must be > 0).
        battery_capacity_kwh: Battery capacity per vehicle in kWh
            (must be > 0).
        energy_consumption_kwh_per_km: Energy consumption rate in kWh/km
            (default 0.25 for a bus).
        charging_window_hours: Available overnight charging window in hours
            (default 8.0).
        charger_utilization_target: Target utilization factor between 0 and 1
            (default 0.75, i.e., 75%).
        preferred_charger_type: Key from ``CHARGER_SPECS`` (default
            ``"dc_50kw"``).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``charger_type`` -- selected charger type key
        - ``charger_count`` -- number of chargers needed
        - ``power_per_charger_kw`` -- rated power per charger
        - ``total_installed_power_kw`` -- charger_count * power
        - ``daily_energy_demand_kwh`` -- fleet-wide daily demand
        - ``daily_energy_per_vehicle_kwh`` -- per-vehicle daily demand
        - ``vehicles_per_charger`` -- vehicles serviced by each charger
        - ``hardware_cost_mad`` -- total charger hardware cost
        - ``installation_cost_mad`` -- total installation cost
        - ``transformer_cost_mad`` -- transformer cost (0 if < 100 kW)
        - ``grid_connection_cost_mad`` -- grid connection fee
        - ``annual_electricity_cost_mad`` -- using blended ONEE tariff
        - ``total_capex_mad`` -- sum of all capital costs
        - ``currency`` -- currency code

    Raises:
        ValueError: If inputs violate business constraints or charger type
            is not recognised.
    """
    # ---- Input validation ------------------------------------------------
    if fleet_size < 1:
        raise ValueError(f"fleet_size must be >= 1, got {fleet_size}")
    if daily_km_per_vehicle <= 0:
        raise ValueError(
            f"daily_km_per_vehicle must be positive, got {daily_km_per_vehicle}"
        )
    if battery_capacity_kwh <= 0:
        raise ValueError(
            f"battery_capacity_kwh must be positive, got {battery_capacity_kwh}"
        )
    if energy_consumption_kwh_per_km <= 0:
        raise ValueError(
            f"energy_consumption_kwh_per_km must be positive, "
            f"got {energy_consumption_kwh_per_km}"
        )
    if charging_window_hours <= 0:
        raise ValueError(
            f"charging_window_hours must be positive, got {charging_window_hours}"
        )
    if not (0.0 < charger_utilization_target <= 1.0):
        raise ValueError(
            f"charger_utilization_target must be in (0, 1], "
            f"got {charger_utilization_target}"
        )
    if preferred_charger_type not in CHARGER_SPECS:
        raise ValueError(
            f"Unknown charger type '{preferred_charger_type}'. "
            f"Valid types: {list(CHARGER_SPECS.keys())}"
        )

    spec = CHARGER_SPECS[preferred_charger_type]
    charger_power = _to_dec(spec["power_kw"])
    unit_cost = _to_dec(spec["cost_mad"])
    install_unit_cost = _to_dec(spec["install_cost_mad"])

    # ---- Sizing calculations ---------------------------------------------
    consumption = _to_dec(energy_consumption_kwh_per_km)
    daily_km = _to_dec(daily_km_per_vehicle)
    window = _to_dec(charging_window_hours)
    utilization = _to_dec(charger_utilization_target)
    fleet = _to_dec(fleet_size)

    # Step 1: daily energy per vehicle
    daily_energy_per_vehicle = _q(daily_km * consumption)

    # Guard against impossible charging scenario
    if daily_energy_per_vehicle <= Decimal("0"):
        raise ValueError(
            "daily_energy_per_vehicle computed as zero or negative"
        )

    # Step 2: vehicles per charger
    # How much energy a single charger can deliver in the window
    energy_per_charger = _q(window * charger_power)
    # How many vehicles that can serve, accounting for utilization
    vehicles_per_charger = _q(
        energy_per_charger / daily_energy_per_vehicle * utilization
    )

    if vehicles_per_charger <= Decimal("0"):
        vehicles_per_charger = Decimal("1")

    # Step 3: charger count (ceiling division)
    charger_count_dec = fleet / vehicles_per_charger
    charger_count = int(math.ceil(float(charger_count_dec)))

    # Ensure at least 1 charger
    if charger_count < 1:
        charger_count = 1

    charger_count_d = _to_dec(charger_count)

    # ---- Power totals ----------------------------------------------------
    total_installed_power = _q(charger_count_d * charger_power)

    # ---- Fleet energy demand ---------------------------------------------
    daily_energy_demand = _q(fleet * daily_energy_per_vehicle)
    # Annual: assume 300 operating days (Moroccan industrial calendar)
    annual_energy_demand = _q(daily_energy_demand * Decimal("300"))
    annual_electricity_cost = _q(annual_energy_demand * ONEE_BLENDED_TARIFF_MAD_KWH)

    # ---- Cost breakdown --------------------------------------------------
    hardware_cost = _q(charger_count_d * unit_cost)
    installation_cost = _q(charger_count_d * install_unit_cost)

    # Transformer: required if total installed power > 100 kW
    transformer_cost = (
        Decimal("150000") if total_installed_power > Decimal("100")
        else Decimal("0")
    )

    # Grid connection: base fee + per-kW fee
    grid_connection_cost = _q(
        Decimal("20000") + Decimal("500") * total_installed_power
    )

    total_capex = _q(
        hardware_cost + installation_cost + transformer_cost + grid_connection_cost
    )

    logger.info(
        "IRVE sizing computed: %d x %s chargers (%s kW total) for %d vehicles, "
        "CAPEX=%s %s, annual electricity=%s %s",
        charger_count,
        preferred_charger_type,
        total_installed_power,
        fleet_size,
        total_capex,
        currency,
        annual_electricity_cost,
        currency,
    )

    return {
        "charger_type": preferred_charger_type,
        "charger_count": charger_count,
        "power_per_charger_kw": float(charger_power),
        "total_installed_power_kw": float(total_installed_power),
        "daily_energy_demand_kwh": float(daily_energy_demand),
        "daily_energy_per_vehicle_kwh": float(daily_energy_per_vehicle),
        "vehicles_per_charger": float(vehicles_per_charger),
        "hardware_cost_mad": float(hardware_cost),
        "installation_cost_mad": float(installation_cost),
        "transformer_cost_mad": float(transformer_cost),
        "grid_connection_cost_mad": float(grid_connection_cost),
        "annual_electricity_cost_mad": float(annual_electricity_cost),
        "total_capex_mad": float(total_capex),
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Part 3: IRVE cost calculator (detailed breakdown with TCO projections)
# ---------------------------------------------------------------------------


def compute_irve_costs(
    charger_count: int,
    charger_type: str = "dc_50kw",
    annual_energy_kwh: float = 0.0,
    currency: str = "MAD",
) -> dict:
    """Compute detailed IRVE cost breakdown with 5-year and 10-year TCO.

    Provides a standalone cost calculator that can be used independently
    of the sizing function. Useful for scenario comparisons and budget
    planning.

    Capital costs:
        - Hardware: unit cost * charger_count
        - Installation: install cost * charger_count
        - Transformer: 150,000 MAD if total power > 100 kW, else 0
        - Grid connection: 20,000 MAD base + 500 MAD per kW installed

    Operating costs (annual):
        - Electricity: annual_energy_kwh * blended ONEE tariff (1.07 MAD/kWh)
        - Maintenance: 3% of hardware cost per year

    TCO projections:
        - 5-year TCO: CAPEX + 5 * annual OPEX
        - 10-year TCO: CAPEX + 10 * annual OPEX

    Args:
        charger_count: Number of chargers (must be >= 1).
        charger_type: Key from ``CHARGER_SPECS`` (default ``"dc_50kw"``).
        annual_energy_kwh: Expected annual energy consumption in kWh
            (default 0.0).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``hardware_cost`` -- total charger hardware cost
        - ``installation_cost`` -- total installation cost
        - ``transformer_cost`` -- transformer upgrade cost (0 if < 100 kW)
        - ``grid_connection_cost`` -- grid connection fee
        - ``annual_electricity_cost`` -- annual electricity cost
        - ``annual_maintenance_cost`` -- 3% of hardware cost
        - ``total_capex`` -- sum of all capital costs
        - ``annual_opex`` -- annual electricity + maintenance
        - ``5_year_tco`` -- CAPEX + 5 years of OPEX
        - ``10_year_tco`` -- CAPEX + 10 years of OPEX
        - ``currency`` -- currency code

    Raises:
        ValueError: If inputs violate business constraints or charger type
            is not recognised.
    """
    # ---- Input validation ------------------------------------------------
    if charger_count < 1:
        raise ValueError(f"charger_count must be >= 1, got {charger_count}")
    if charger_type not in CHARGER_SPECS:
        raise ValueError(
            f"Unknown charger type '{charger_type}'. "
            f"Valid types: {list(CHARGER_SPECS.keys())}"
        )
    if annual_energy_kwh < 0:
        raise ValueError(
            f"annual_energy_kwh must be non-negative, got {annual_energy_kwh}"
        )

    spec = CHARGER_SPECS[charger_type]
    charger_power = _to_dec(spec["power_kw"])
    unit_cost = _to_dec(spec["cost_mad"])
    install_unit_cost = _to_dec(spec["install_cost_mad"])
    count = _to_dec(charger_count)

    # ---- Capital costs ---------------------------------------------------
    hardware_cost = _q(count * unit_cost)
    installation_cost = _q(count * install_unit_cost)

    total_installed_power = _q(count * charger_power)

    # Transformer: required if total installed power > 100 kW
    transformer_cost = (
        Decimal("150000") if total_installed_power > Decimal("100")
        else Decimal("0")
    )

    # Grid connection: base fee + per-kW fee
    grid_connection_cost = _q(
        Decimal("20000") + Decimal("500") * total_installed_power
    )

    total_capex = _q(
        hardware_cost + installation_cost + transformer_cost + grid_connection_cost
    )

    # ---- Operating costs -------------------------------------------------
    annual_energy = _to_dec(annual_energy_kwh)
    annual_electricity_cost = _q(annual_energy * ONEE_BLENDED_TARIFF_MAD_KWH)

    # Maintenance: 3% of hardware cost annually (industry standard for IRVE)
    maintenance_rate = Decimal("0.03")
    annual_maintenance_cost = _q(hardware_cost * maintenance_rate)

    annual_opex = _q(annual_electricity_cost + annual_maintenance_cost)

    # ---- TCO projections -------------------------------------------------
    tco_5_year = _q(total_capex + Decimal("5") * annual_opex)
    tco_10_year = _q(total_capex + Decimal("10") * annual_opex)

    logger.info(
        "IRVE costs computed: %d x %s, CAPEX=%s %s, annual OPEX=%s %s, "
        "5y TCO=%s %s, 10y TCO=%s %s",
        charger_count,
        charger_type,
        total_capex,
        currency,
        annual_opex,
        currency,
        tco_5_year,
        currency,
        tco_10_year,
        currency,
    )

    return {
        "hardware_cost": float(hardware_cost),
        "installation_cost": float(installation_cost),
        "transformer_cost": float(transformer_cost),
        "grid_connection_cost": float(grid_connection_cost),
        "annual_electricity_cost": float(annual_electricity_cost),
        "annual_maintenance_cost": float(annual_maintenance_cost),
        "total_capex": float(total_capex),
        "annual_opex": float(annual_opex),
        "5_year_tco": float(tco_5_year),
        "10_year_tco": float(tco_10_year),
        "currency": currency,
    }
