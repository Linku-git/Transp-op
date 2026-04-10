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
# Correction factor lookup tables (CDC SOTREG v5.0)
# ---------------------------------------------------------------------------

K_PENTE_TABLE: dict[str, Decimal] = {
    "flat": Decimal("1.0"),         # 0-2% slope
    "moderate": Decimal("1.1"),     # 2-5% slope
    "hilly": Decimal("1.3"),        # 5-8% slope
    "mountainous": Decimal("1.6"),  # >8% slope
}

K_SAISON_TABLE: dict[str, Decimal] = {
    "temperate": Decimal("1.0"),    # 15-25 C
    "hot": Decimal("1.1"),          # >35 C
    "cold": Decimal("1.15"),        # <5 C
    "extreme": Decimal("1.3"),      # <-10 C or >45 C
}

K_VITESSE_TABLE: dict[str, Decimal] = {
    "optimal": Decimal("0.95"),     # 30-50 km/h
    "moderate": Decimal("1.0"),     # 50-70 km/h
    "city": Decimal("1.1"),         # <30 km/h
    "highway": Decimal("1.25"),     # >70 km/h
}


# ---------------------------------------------------------------------------
# Factor accessors
# ---------------------------------------------------------------------------

def get_k_pente(profile: str) -> Decimal:
    """Return the slope correction factor for the given terrain profile.

    Args:
        profile: One of ``flat``, ``moderate``, ``hilly``, ``mountainous``.

    Returns:
        Decimal correction factor.

    Raises:
        ValueError: If *profile* is not a recognised key.
    """
    key = profile.lower().strip()
    if key not in K_PENTE_TABLE:
        raise ValueError(
            f"Unknown pente profile '{profile}'. "
            f"Valid values: {list(K_PENTE_TABLE.keys())}"
        )
    return K_PENTE_TABLE[key]


def get_k_saison(profile: str) -> Decimal:
    """Return the seasonal correction factor for the given climate profile.

    Args:
        profile: One of ``temperate``, ``hot``, ``cold``, ``extreme``.

    Returns:
        Decimal correction factor.

    Raises:
        ValueError: If *profile* is not a recognised key.
    """
    key = profile.lower().strip()
    if key not in K_SAISON_TABLE:
        raise ValueError(
            f"Unknown saison profile '{profile}'. "
            f"Valid values: {list(K_SAISON_TABLE.keys())}"
        )
    return K_SAISON_TABLE[key]


def get_k_vitesse(profile: str) -> Decimal:
    """Return the speed correction factor for the given speed profile.

    Args:
        profile: One of ``optimal``, ``moderate``, ``city``, ``highway``.

    Returns:
        Decimal correction factor.

    Raises:
        ValueError: If *profile* is not a recognised key.
    """
    key = profile.lower().strip()
    if key not in K_VITESSE_TABLE:
        raise ValueError(
            f"Unknown vitesse profile '{profile}'. "
            f"Valid values: {list(K_VITESSE_TABLE.keys())}"
        )
    return K_VITESSE_TABLE[key]


# ---------------------------------------------------------------------------
# Range correction
# ---------------------------------------------------------------------------

def compute_corrected_range(
    nominal_range_km: float,
    pente_profile: str = "flat",
    saison_profile: str = "temperate",
    vitesse_profile: str = "moderate",
) -> dict:
    """Compute corrected range with all 3 CDC correction factors.

    Formula::

        corrected_range = nominal_range / (k_pente * k_saison * k_vitesse)

    Args:
        nominal_range_km: Manufacturer-stated range in km (must be > 0).
        pente_profile: Terrain profile key for slope factor.
        saison_profile: Climate profile key for seasonal factor.
        vitesse_profile: Speed profile key for speed factor.

    Returns:
        Dict containing:
        - ``nominal_range_km`` -- the input range
        - ``k_pente``, ``k_saison``, ``k_vitesse`` -- individual factors
        - ``correction_factor`` -- product of the three factors
        - ``corrected_range_km`` -- nominal / correction_factor
        - ``range_reduction_pct`` -- percentage of range lost
        - ``currency`` -- always ``"MAD"``

    Raises:
        ValueError: If *nominal_range_km* is non-positive or a profile is
            not recognised.
    """
    if nominal_range_km <= 0:
        raise ValueError(
            f"nominal_range_km must be positive, got {nominal_range_km}"
        )

    k_p = get_k_pente(pente_profile)
    k_s = get_k_saison(saison_profile)
    k_v = get_k_vitesse(vitesse_profile)

    nominal = _to_dec(nominal_range_km)
    correction_factor = k_p * k_s * k_v
    corrected = _q(nominal / correction_factor)
    reduction_pct = _q(
        (Decimal("1") - Decimal("1") / correction_factor) * Decimal("100")
    )

    logger.info(
        "Range correction: %.1f km -> %s km "
        "(k_pente=%s, k_saison=%s, k_vitesse=%s, factor=%s)",
        nominal_range_km,
        corrected,
        k_p,
        k_s,
        k_v,
        _q(correction_factor),
    )

    return {
        "nominal_range_km": float(nominal),
        "k_pente": float(k_p),
        "k_saison": float(k_s),
        "k_vitesse": float(k_v),
        "correction_factor": float(_q(correction_factor)),
        "corrected_range_km": float(corrected),
        "range_reduction_pct": float(reduction_pct),
        "currency": "MAD",
    }


# ---------------------------------------------------------------------------
# 15-year TCO with financing
# ---------------------------------------------------------------------------

def compute_tco_15year(
    purchase_price: float,
    annual_maintenance_cost: float,
    energy_cost_per_km: float,
    annual_km: float,
    residual_value_pct: float = 10.0,
    duration_years: int = 15,
    loan_rate_pct: float = 5.0,
    loan_duration_years: int = 7,
    energy_escalation_pct: float = 3.0,
    maintenance_escalation_pct: float = 2.0,
    currency: str = "MAD",
) -> dict:
    """Compute 15-year Total Cost of Ownership with financing.

    Financial model:

    * **Depreciation**: linear over *duration_years*.
    * **Financing**: simple interest on *purchase_price* at *loan_rate_pct*
      for each year up to *loan_duration_years*.
    * **Energy**: ``energy_cost_per_km * annual_km`` in year 1, compounding
      annually at *energy_escalation_pct*.
    * **Maintenance**: ``annual_maintenance_cost`` in year 1, compounding
      annually at *maintenance_escalation_pct*.
    * **Residual value**: subtracted at end of period.

    Args:
        purchase_price: Vehicle purchase price (MAD).
        annual_maintenance_cost: Year-1 annual maintenance cost (MAD).
        energy_cost_per_km: Year-1 energy cost per km (MAD/km).
        annual_km: Annual distance driven (km).
        residual_value_pct: Residual value as % of purchase price.
        duration_years: TCO horizon in years.
        loan_rate_pct: Annual loan interest rate (%).
        loan_duration_years: Loan repayment period (years).
        energy_escalation_pct: Annual energy price increase (%).
        maintenance_escalation_pct: Annual maintenance cost increase (%).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict with ``total_tco``, ``yearly_breakdown``, ``financing_total``,
        ``energy_total``, ``maintenance_total``, ``depreciation_total``,
        ``residual_value``, and ``currency``.

    Raises:
        ValueError: If any input violates business constraints.
    """
    # ---- Input validation ------------------------------------------------
    if purchase_price <= 0:
        raise ValueError(
            f"purchase_price must be positive, got {purchase_price}"
        )
    if annual_maintenance_cost < 0:
        raise ValueError(
            f"annual_maintenance_cost must be non-negative, got "
            f"{annual_maintenance_cost}"
        )
    if energy_cost_per_km < 0:
        raise ValueError(
            f"energy_cost_per_km must be non-negative, got {energy_cost_per_km}"
        )
    if annual_km <= 0:
        raise ValueError(f"annual_km must be positive, got {annual_km}")
    if duration_years < 1:
        raise ValueError(
            f"duration_years must be >= 1, got {duration_years}"
        )
    if loan_duration_years < 0:
        raise ValueError(
            f"loan_duration_years must be non-negative, got {loan_duration_years}"
        )
    if not (0 <= residual_value_pct <= 100):
        raise ValueError(
            f"residual_value_pct must be between 0 and 100, got "
            f"{residual_value_pct}"
        )

    # ---- Decimal conversion ----------------------------------------------
    price = _to_dec(purchase_price)
    maint_base = _to_dec(annual_maintenance_cost)
    energy_base = _to_dec(energy_cost_per_km) * _to_dec(annual_km)
    residual_rate = _to_dec(residual_value_pct) / Decimal("100")
    residual_value = _q(price * residual_rate)
    depreciation_total = _q(price - residual_value)
    annual_depreciation = _q(depreciation_total / _to_dec(duration_years))
    loan_rate = _to_dec(loan_rate_pct) / Decimal("100")
    energy_esc = Decimal("1") + _to_dec(energy_escalation_pct) / Decimal("100")
    maint_esc = Decimal("1") + _to_dec(maintenance_escalation_pct) / Decimal("100")

    # ---- Year-by-year computation ----------------------------------------
    yearly_breakdown: list[dict] = []
    cumulative_tco = Decimal("0")
    financing_total = Decimal("0")
    energy_total = Decimal("0")
    maintenance_total = Decimal("0")

    for year in range(1, duration_years + 1):
        # Financing: simple interest for years within loan period
        if year <= loan_duration_years:
            financing = _q(price * loan_rate)
        else:
            financing = Decimal("0")

        # Energy cost with escalation (year 1 = base, year 2 = base * esc, ...)
        energy = _q(energy_base * energy_esc ** (year - 1))

        # Maintenance with escalation
        maintenance = _q(maint_base * maint_esc ** (year - 1))

        year_total = _q(annual_depreciation + financing + energy + maintenance)
        cumulative_tco += year_total

        financing_total += financing
        energy_total += energy
        maintenance_total += maintenance

        yearly_breakdown.append({
            "year": year,
            "depreciation": float(annual_depreciation),
            "maintenance": float(maintenance),
            "energy": float(energy),
            "financing": float(financing),
            "year_total": float(year_total),
            "cumulative_tco": float(_q(cumulative_tco)),
        })

    total_tco = _q(cumulative_tco)

    logger.info(
        "15-year TCO computed: total=%s %s over %d years "
        "(financing=%s, energy=%s, maintenance=%s, depreciation=%s)",
        total_tco,
        currency,
        duration_years,
        _q(financing_total),
        _q(energy_total),
        _q(maintenance_total),
        depreciation_total,
    )

    return {
        "total_tco": float(total_tco),
        "yearly_breakdown": yearly_breakdown,
        "financing_total": float(_q(financing_total)),
        "energy_total": float(_q(energy_total)),
        "maintenance_total": float(_q(maintenance_total)),
        "depreciation_total": float(depreciation_total),
        "residual_value": float(residual_value),
        "duration_years": duration_years,
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Electrification breakeven
# ---------------------------------------------------------------------------

def compute_electrification_breakeven(
    capex_diesel: float,
    capex_electric: float,
    opex_per_km_diesel: float,
    opex_per_km_electric: float,
    annual_km_reference: float = 40000.0,
    currency: str = "MAD",
) -> dict:
    """Compute the breakeven annual km where electric becomes cheaper.

    Formula::

        km_seuil = delta_capex / delta_opex_per_km

    where:
    * ``delta_capex = capex_electric - capex_diesel``  (electric is more
      expensive upfront)
    * ``delta_opex_per_km = opex_per_km_diesel - opex_per_km_electric``
      (diesel is more expensive per km to operate)

    CDC reference: approximately 48,500 km/an for OCP fleet parameters.

    Args:
        capex_diesel: Purchase cost of a diesel vehicle (MAD).
        capex_electric: Purchase cost of an electric vehicle (MAD).
        opex_per_km_diesel: Operating cost per km for diesel (MAD/km).
        opex_per_km_electric: Operating cost per km for electric (MAD/km).
        annual_km_reference: Reference annual km for payback calculation
            (default 40,000 km).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict with ``km_seuil``, ``delta_capex``, ``delta_opex_per_km``,
        ``payback_years_at_reference_km``, ``is_electric_viable``,
        and ``currency``.

    Raises:
        ValueError: If inputs violate business constraints or breakeven
            cannot be computed (delta_opex <= 0).
    """
    if capex_diesel <= 0:
        raise ValueError(
            f"capex_diesel must be positive, got {capex_diesel}"
        )
    if capex_electric <= 0:
        raise ValueError(
            f"capex_electric must be positive, got {capex_electric}"
        )
    if opex_per_km_diesel < 0:
        raise ValueError(
            f"opex_per_km_diesel must be non-negative, got {opex_per_km_diesel}"
        )
    if opex_per_km_electric < 0:
        raise ValueError(
            f"opex_per_km_electric must be non-negative, got "
            f"{opex_per_km_electric}"
        )
    if annual_km_reference <= 0:
        raise ValueError(
            f"annual_km_reference must be positive, got {annual_km_reference}"
        )

    d_capex = _to_dec(capex_electric) - _to_dec(capex_diesel)
    d_opex = _to_dec(opex_per_km_diesel) - _to_dec(opex_per_km_electric)

    # If electric is cheaper upfront, breakeven is immediate
    if d_capex <= 0:
        logger.info(
            "Electric CAPEX <= diesel CAPEX (%s <= %s %s): "
            "electric is immediately viable",
            capex_electric,
            capex_diesel,
            currency,
        )
        return {
            "km_seuil": 0.0,
            "delta_capex": float(_q(d_capex)),
            "delta_opex_per_km": float(_q(d_opex)),
            "payback_years_at_reference_km": 0.0,
            "is_electric_viable": True,
            "annual_km_reference": annual_km_reference,
            "currency": currency,
        }

    # If diesel is NOT more expensive per km, breakeven never occurs
    if d_opex <= 0:
        logger.warning(
            "Diesel OPEX/km <= electric OPEX/km (%s <= %s): "
            "breakeven is unreachable",
            opex_per_km_diesel,
            opex_per_km_electric,
        )
        return {
            "km_seuil": None,
            "delta_capex": float(_q(d_capex)),
            "delta_opex_per_km": float(_q(d_opex)),
            "payback_years_at_reference_km": None,
            "is_electric_viable": False,
            "annual_km_reference": annual_km_reference,
            "currency": currency,
        }

    km_seuil = _q(d_capex / d_opex)
    ref_km = _to_dec(annual_km_reference)
    payback_years = _q(km_seuil / ref_km) if ref_km > 0 else None

    is_viable = km_seuil <= ref_km

    logger.info(
        "Electrification breakeven: %s km/an (delta_capex=%s %s, "
        "delta_opex=%s %s/km, payback=%.1f years at %s km/an)",
        km_seuil,
        _q(d_capex),
        currency,
        _q(d_opex),
        currency,
        float(payback_years) if payback_years is not None else 0.0,
        ref_km,
    )

    return {
        "km_seuil": float(km_seuil),
        "delta_capex": float(_q(d_capex)),
        "delta_opex_per_km": float(_q(d_opex)),
        "payback_years_at_reference_km": float(payback_years) if payback_years is not None else None,
        "is_electric_viable": is_viable,
        "annual_km_reference": annual_km_reference,
        "currency": currency,
    }
