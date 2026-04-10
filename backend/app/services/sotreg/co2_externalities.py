from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Carbon pricing constants (Morocco context)
# ---------------------------------------------------------------------------

# Morocco carbon tax discussions: 100-300 MAD/tCO2 range
DEFAULT_CARBON_PRICE_MAD_TCO2 = Decimal("200")  # 200 MAD per tCO2
# EU ETS reference for international benchmarking
EU_ETS_REFERENCE_EUR = Decimal("80")  # EUR 80/tCO2
EUR_TO_MAD = Decimal("10.8")  # approximate exchange rate

# ---------------------------------------------------------------------------
# Emission factors (kgCO2/km by motorization)
# ---------------------------------------------------------------------------

EMISSION_FACTORS_KG_CO2_PER_KM: dict[str, Decimal] = {
    "diesel": Decimal("0.89"),      # average for transport bus/coach
    "essence": Decimal("0.85"),     # gasoline
    "gnv": Decimal("0.65"),         # compressed natural gas
    "hybride": Decimal("0.55"),     # diesel-electric hybrid
    "electrique": Decimal("0.0"),   # zero tailpipe
    "hydrogen": Decimal("0.0"),     # zero tailpipe (fuel cell)
}

# Grid emission factor for Morocco (ONEE electricity mix)
# Source: IEA / ONEE annual report — coal + gas + renewables mix
GRID_FACTOR_KG_CO2_PER_KWH = Decimal("0.72")  # Morocco grid average

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_dec(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


def _get_emission_factor(motorization: str) -> Decimal:
    """Retrieve the emission factor for a given motorization type.

    Args:
        motorization: One of ``diesel``, ``essence``, ``gnv``, ``hybride``,
            ``electrique``, ``hydrogen``.

    Returns:
        Emission factor in kgCO2/km.

    Raises:
        ValueError: If *motorization* is not a recognised key.
    """
    key = motorization.lower().strip()
    if key not in EMISSION_FACTORS_KG_CO2_PER_KM:
        raise ValueError(
            f"Unknown motorization '{motorization}'. "
            f"Valid values: {list(EMISSION_FACTORS_KG_CO2_PER_KM.keys())}"
        )
    return EMISSION_FACTORS_KG_CO2_PER_KM[key]


# ---------------------------------------------------------------------------
# CO2 valorization
# ---------------------------------------------------------------------------


def compute_co2_valorization(
    fleet_annual_km: float,
    current_motorization: str = "diesel",
    target_motorization: str = "electrique",
    carbon_price_mad_tco2: float = 200.0,
    vehicle_count: int = 1,
    energy_consumption_kwh_per_km: float = 0.25,
    currency: str = "MAD",
) -> dict:
    """Monetize avoided CO2 emissions from a fleet motorization transition.

    Logic:

    1. ``current_emissions = fleet_km * emission_factor[current] * count``
    2. For electric/hydrogen targets, well-to-wheel emissions from grid
       electricity are included:
       ``target_emissions = fleet_km * grid_factor * consumption * count``
    3. For other targets, direct tailpipe factor is used:
       ``target_emissions = fleet_km * emission_factor[target] * count``
    4. ``avoided_tco2 = (current - target) / 1000``
    5. ``valorization = avoided_tco2 * carbon_price``

    Args:
        fleet_annual_km: Annual distance per vehicle (km).
            Must be >= 0.
        current_motorization: Current fuel type.
        target_motorization: Target fuel type after transition.
        carbon_price_mad_tco2: Carbon price in MAD per tonne CO2.
        vehicle_count: Number of vehicles in the transition.
            Must be >= 1.
        energy_consumption_kwh_per_km: Electricity consumption for
            electric/hydrogen targets (kWh/km, default 0.25).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``current_emissions_tco2`` -- annual emissions before transition
        - ``target_emissions_tco2`` -- annual emissions after transition
        - ``avoided_emissions_tco2`` -- difference (current - target)
        - ``carbon_price_mad_tco2`` -- price used
        - ``valorization_mad`` -- annual monetary value of avoided CO2
        - ``valorization_15year_mad`` -- 15-year undiscounted total
        - ``fleet_annual_km``, ``vehicle_count``
        - ``current_motorization``, ``target_motorization``
        - ``currency``

    Raises:
        ValueError: If inputs violate constraints.
    """
    if fleet_annual_km < 0:
        raise ValueError(
            f"fleet_annual_km must be non-negative, got {fleet_annual_km}"
        )
    if vehicle_count < 1:
        raise ValueError(
            f"vehicle_count must be >= 1, got {vehicle_count}"
        )
    if carbon_price_mad_tco2 < 0:
        raise ValueError(
            f"carbon_price_mad_tco2 must be non-negative, got "
            f"{carbon_price_mad_tco2}"
        )
    if energy_consumption_kwh_per_km < 0:
        raise ValueError(
            f"energy_consumption_kwh_per_km must be non-negative, got "
            f"{energy_consumption_kwh_per_km}"
        )

    # Zero fleet km => zero everything
    if fleet_annual_km == 0:
        logger.info("Fleet annual km is 0 -- no emissions to compute")
        return {
            "current_emissions_tco2": 0.0,
            "target_emissions_tco2": 0.0,
            "avoided_emissions_tco2": 0.0,
            "carbon_price_mad_tco2": carbon_price_mad_tco2,
            "valorization_mad": 0.0,
            "valorization_15year_mad": 0.0,
            "fleet_annual_km": fleet_annual_km,
            "vehicle_count": vehicle_count,
            "current_motorization": current_motorization,
            "target_motorization": target_motorization,
            "currency": currency,
        }

    km = _to_dec(fleet_annual_km)
    count = _to_dec(vehicle_count)
    price = _to_dec(carbon_price_mad_tco2)

    # Current emissions (kgCO2)
    current_factor = _get_emission_factor(current_motorization)
    current_kg = km * current_factor * count

    # Target emissions (kgCO2)
    target_key = target_motorization.lower().strip()
    if target_key in ("electrique", "hydrogen"):
        # Well-to-wheel: grid emissions from electricity generation
        consumption = _to_dec(energy_consumption_kwh_per_km)
        target_kg = km * GRID_FACTOR_KG_CO2_PER_KWH * consumption * count
    else:
        target_factor = _get_emission_factor(target_motorization)
        target_kg = km * target_factor * count

    # Convert kg to tonnes
    current_tco2 = _q(current_kg / Decimal("1000"))
    target_tco2 = _q(target_kg / Decimal("1000"))
    avoided_tco2 = _q(current_tco2 - target_tco2)

    # Monetize
    valorization = _q(avoided_tco2 * price)
    valorization_15y = _q(valorization * Decimal("15"))

    logger.info(
        "CO2 valorization: %s -> %s, avoided=%s tCO2/yr, "
        "value=%s %s/yr (%s %s over 15y), fleet=%s km * %d vehicles",
        current_motorization,
        target_motorization,
        avoided_tco2,
        valorization,
        currency,
        valorization_15y,
        currency,
        km,
        vehicle_count,
    )

    return {
        "current_emissions_tco2": float(current_tco2),
        "target_emissions_tco2": float(target_tco2),
        "avoided_emissions_tco2": float(avoided_tco2),
        "carbon_price_mad_tco2": carbon_price_mad_tco2,
        "valorization_mad": float(valorization),
        "valorization_15year_mad": float(valorization_15y),
        "fleet_annual_km": fleet_annual_km,
        "vehicle_count": vehicle_count,
        "current_motorization": current_motorization,
        "target_motorization": target_motorization,
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# NPV of CO2 savings with escalating carbon price
# ---------------------------------------------------------------------------


def compute_co2_savings_npv(
    fleet_annual_km: float,
    current_motorization: str = "diesel",
    target_motorization: str = "electrique",
    carbon_price_mad_tco2: float = 200.0,
    carbon_price_escalation_pct: float = 3.0,
    discount_rate: float = 0.08,
    horizon_years: int = 15,
    vehicle_count: int = 1,
    energy_consumption_kwh_per_km: float = 0.25,
    currency: str = "MAD",
) -> dict:
    """Compute the NPV of CO2 savings over a multi-year horizon.

    The carbon price escalates annually, and future savings are discounted
    back to present value.

    For each year *t* (1 .. horizon):

    1. ``carbon_price_t = base_price * (1 + escalation)^(t-1)``
    2. ``avoided_tco2`` is computed once (constant fleet).
    3. ``savings_t = avoided_tco2 * carbon_price_t``
    4. ``pv_t = savings_t / (1 + discount_rate)^t``

    Args:
        fleet_annual_km: Annual distance per vehicle (km).
        current_motorization: Current fuel type.
        target_motorization: Target fuel type.
        carbon_price_mad_tco2: Year-1 carbon price (MAD/tCO2).
        carbon_price_escalation_pct: Annual carbon price increase (%).
        discount_rate: Discount rate for PV calculation.
        horizon_years: Number of years to project.
            Must be >= 1.
        vehicle_count: Number of vehicles.
        energy_consumption_kwh_per_km: Electricity consumption for
            electric targets (kWh/km).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``npv_co2_savings_mad`` -- total NPV of CO2 savings
        - ``yearly_savings`` -- list of dicts per year with ``year``,
          ``carbon_price``, ``avoided_tco2``, ``savings_mad``, ``pv_mad``
        - ``total_avoided_tco2`` -- cumulative avoided tonnes
        - ``horizon_years``, ``discount_rate``
        - ``currency``

    Raises:
        ValueError: If inputs violate constraints.
    """
    if fleet_annual_km < 0:
        raise ValueError(
            f"fleet_annual_km must be non-negative, got {fleet_annual_km}"
        )
    if horizon_years < 1:
        raise ValueError(
            f"horizon_years must be >= 1, got {horizon_years}"
        )
    if discount_rate < 0:
        raise ValueError(
            f"discount_rate must be non-negative, got {discount_rate}"
        )
    if vehicle_count < 1:
        raise ValueError(
            f"vehicle_count must be >= 1, got {vehicle_count}"
        )

    # Zero fleet km => zero savings
    if fleet_annual_km == 0:
        logger.info("Fleet annual km is 0 -- no CO2 savings NPV to compute")
        return {
            "npv_co2_savings_mad": 0.0,
            "yearly_savings": [],
            "total_avoided_tco2": 0.0,
            "horizon_years": horizon_years,
            "discount_rate": discount_rate,
            "currency": currency,
        }

    # Compute annual avoided emissions (constant across years)
    km = _to_dec(fleet_annual_km)
    count = _to_dec(vehicle_count)

    current_factor = _get_emission_factor(current_motorization)
    current_kg = km * current_factor * count

    target_key = target_motorization.lower().strip()
    if target_key in ("electrique", "hydrogen"):
        consumption = _to_dec(energy_consumption_kwh_per_km)
        target_kg = km * GRID_FACTOR_KG_CO2_PER_KWH * consumption * count
    else:
        target_factor = _get_emission_factor(target_motorization)
        target_kg = km * target_factor * count

    avoided_tco2_annual = (current_kg - target_kg) / Decimal("1000")

    # Year-by-year computation
    base_price = _to_dec(carbon_price_mad_tco2)
    escalation = Decimal("1") + _to_dec(carbon_price_escalation_pct) / Decimal("100")
    r = _to_dec(discount_rate)
    one_plus_r = Decimal("1") + r

    yearly_savings: list[dict] = []
    npv_acc = Decimal("0")
    total_avoided = Decimal("0")

    for year in range(1, horizon_years + 1):
        # Escalated carbon price
        price_t = _q(base_price * escalation ** (year - 1))

        # Annual savings
        savings = _q(avoided_tco2_annual * price_t)

        # Discount to present value
        if r == Decimal("0"):
            pv = savings
        else:
            discount_factor = one_plus_r ** year
            pv = _q(savings / discount_factor)

        npv_acc += pv
        total_avoided += avoided_tco2_annual

        yearly_savings.append({
            "year": year,
            "carbon_price": float(price_t),
            "avoided_tco2": float(_q(avoided_tco2_annual)),
            "savings_mad": float(savings),
            "pv_mad": float(pv),
        })

    npv_final = _q(npv_acc)
    total_avoided_final = _q(total_avoided)

    logger.info(
        "CO2 savings NPV: %s %s over %d years "
        "(avoided=%s tCO2 total, rate=%.2f%%, escalation=%.1f%%)",
        npv_final,
        currency,
        horizon_years,
        total_avoided_final,
        discount_rate * 100,
        carbon_price_escalation_pct,
    )

    return {
        "npv_co2_savings_mad": float(npv_final),
        "yearly_savings": yearly_savings,
        "total_avoided_tco2": float(total_avoided_final),
        "horizon_years": horizon_years,
        "discount_rate": discount_rate,
        "currency": currency,
    }
