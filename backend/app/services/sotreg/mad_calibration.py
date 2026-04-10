from __future__ import annotations

import logging
from datetime import date
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
# Exchange rates — Bank Al-Maghrib (BAM) reference, April 2026
# ---------------------------------------------------------------------------

EXCHANGE_RATES: dict[str, Decimal] = {
    "EUR_MAD": Decimal("10.80"),
    "USD_MAD": Decimal("9.95"),
    "GBP_MAD": Decimal("12.60"),
}

# Reverse lookup for convert_from_mad
_REVERSE_KEYS: dict[str, str] = {
    "EUR": "EUR_MAD",
    "USD": "USD_MAD",
    "GBP": "GBP_MAD",
}


# ---------------------------------------------------------------------------
# Morocco macroeconomic parameters
# ---------------------------------------------------------------------------

# HCP (Haut Commissariat au Plan) historical average inflation
MOROCCO_INFLATION_RATE: Decimal = Decimal("0.028")  # 2.8%

# Bank Al-Maghrib base (policy) rate
BAM_BASE_RATE: Decimal = Decimal("0.03")  # 3.0%


# ---------------------------------------------------------------------------
# ONEE (Office National de l'Electricite et de l'Eau Potable) tariff schedule
# Consistent with charging_optimizer.py values
# ---------------------------------------------------------------------------

ONEE_TARIFF_SCHEDULE: dict[str, dict] = {
    "creuse": {
        "rate_mad_kwh": Decimal("0.82"),
        "hours": "22h-07h",
        "description": "Heures creuses",
    },
    "pleine": {
        "rate_mad_kwh": Decimal("1.22"),
        "hours": "07h-17h",
        "description": "Heures pleines",
    },
    "pointe": {
        "rate_mad_kwh": Decimal("1.58"),
        "hours": "17h-22h",
        "description": "Heures de pointe",
    },
}

# Blended average: ~60% creuse, ~30% pleine, ~10% pointe (depot usage pattern)
ONEE_BLENDED_RATE: Decimal = _q(
    Decimal("0.60") * ONEE_TARIFF_SCHEDULE["creuse"]["rate_mad_kwh"]
    + Decimal("0.30") * ONEE_TARIFF_SCHEDULE["pleine"]["rate_mad_kwh"]
    + Decimal("0.10") * ONEE_TARIFF_SCHEDULE["pointe"]["rate_mad_kwh"]
)

# ONEE monthly demand charge per kVA
ONEE_DEMAND_CHARGE_MAD_KVA: Decimal = Decimal("200.0")


# ---------------------------------------------------------------------------
# Currency conversion
# ---------------------------------------------------------------------------


def convert_to_mad(amount: float, source_currency: str = "EUR") -> dict:
    """Convert amount from source currency to MAD.

    Uses Bank Al-Maghrib reference exchange rates.

    Args:
        amount: Amount in source currency (must be non-negative).
        source_currency: ISO 4217 currency code (``EUR``, ``USD``, ``GBP``).

    Returns:
        Dict with ``amount_mad``, ``rate_used``, ``source_currency``,
        ``source_amount``, and ``reference_date``.

    Raises:
        ValueError: If *source_currency* is not supported or *amount*
            is negative.
    """
    if amount < 0:
        raise ValueError(f"amount must be non-negative, got {amount}")

    key = f"{source_currency.upper()}_MAD"
    if key not in EXCHANGE_RATES:
        raise ValueError(
            f"Unsupported source currency '{source_currency}'. "
            f"Supported: {list(_REVERSE_KEYS.keys())}"
        )

    rate = EXCHANGE_RATES[key]
    amount_dec = _to_dec(amount)
    amount_mad = _q(amount_dec * rate)

    logger.info(
        "Currency conversion: %.2f %s -> %s MAD (rate=%s)",
        amount,
        source_currency.upper(),
        amount_mad,
        rate,
    )

    return {
        "amount_mad": float(amount_mad),
        "rate_used": float(rate),
        "source_currency": source_currency.upper(),
        "source_amount": amount,
        "reference_date": date.today().isoformat(),
    }


def convert_from_mad(amount_mad: float, target_currency: str = "EUR") -> dict:
    """Convert MAD amount to target foreign currency.

    Args:
        amount_mad: Amount in MAD (must be non-negative).
        target_currency: ISO 4217 currency code (``EUR``, ``USD``, ``GBP``).

    Returns:
        Dict with ``amount_foreign``, ``rate_used``, ``target_currency``,
        ``amount_mad``, and ``reference_date``.

    Raises:
        ValueError: If *target_currency* is not supported or *amount_mad*
            is negative.
    """
    if amount_mad < 0:
        raise ValueError(f"amount_mad must be non-negative, got {amount_mad}")

    currency_upper = target_currency.upper()
    if currency_upper not in _REVERSE_KEYS:
        raise ValueError(
            f"Unsupported target currency '{target_currency}'. "
            f"Supported: {list(_REVERSE_KEYS.keys())}"
        )

    key = _REVERSE_KEYS[currency_upper]
    rate = EXCHANGE_RATES[key]
    mad_dec = _to_dec(amount_mad)
    amount_foreign = _q(mad_dec / rate)

    logger.info(
        "Currency conversion: %.2f MAD -> %s %s (rate=%s)",
        amount_mad,
        amount_foreign,
        currency_upper,
        rate,
    )

    return {
        "amount_foreign": float(amount_foreign),
        "rate_used": float(rate),
        "target_currency": currency_upper,
        "amount_mad": amount_mad,
        "reference_date": date.today().isoformat(),
    }


# ---------------------------------------------------------------------------
# Inflation adjustment
# ---------------------------------------------------------------------------


def adjust_for_inflation(
    amount_mad: float,
    years: int,
    inflation_rate: float | None = None,
) -> dict:
    """Adjust MAD amount for inflation over N years.

    Computes the nominal future value using compound inflation:

        adjusted = amount_mad * (1 + inflation_rate) ^ years

    Also computes the real value loss percentage (how much purchasing
    power is eroded).

    Args:
        amount_mad: Current-year amount in MAD (must be positive).
        years: Number of years to project (must be >= 0).
        inflation_rate: Annual inflation rate as decimal (e.g. 0.028
            for 2.8%). Defaults to ``MOROCCO_INFLATION_RATE``.

    Returns:
        Dict with ``original``, ``adjusted``, ``inflation_rate``,
        ``years``, ``real_value_loss_pct``, and ``currency``.

    Raises:
        ValueError: If inputs violate constraints.
    """
    if amount_mad <= 0:
        raise ValueError(f"amount_mad must be positive, got {amount_mad}")
    if years < 0:
        raise ValueError(f"years must be non-negative, got {years}")

    rate = _to_dec(inflation_rate) if inflation_rate is not None else MOROCCO_INFLATION_RATE

    if rate < 0:
        raise ValueError(f"inflation_rate must be non-negative, got {inflation_rate}")

    base = _to_dec(amount_mad)
    factor = (Decimal("1") + rate) ** years
    adjusted = _q(base * factor)

    # Real value loss: how much purchasing power the original amount loses
    # In year N, you need `adjusted` MAD to buy what `original` buys today
    # Loss = (adjusted - original) / adjusted * 100
    if adjusted > 0:
        real_value_loss_pct = _q(
            (Decimal("1") - base / adjusted) * Decimal("100")
        )
    else:
        real_value_loss_pct = Decimal("0")

    logger.info(
        "Inflation adjustment: %.2f MAD -> %s MAD over %d years "
        "(rate=%.3f, loss=%.1f%%)",
        amount_mad,
        adjusted,
        years,
        float(rate),
        float(real_value_loss_pct),
    )

    return {
        "original": amount_mad,
        "adjusted": float(adjusted),
        "inflation_rate": float(rate),
        "years": years,
        "real_value_loss_pct": float(real_value_loss_pct),
        "currency": "MAD",
    }


# ---------------------------------------------------------------------------
# Real discount rate (Fisher equation)
# ---------------------------------------------------------------------------


def compute_real_discount_rate(
    nominal_rate: float,
    inflation_rate: float | None = None,
) -> dict:
    """Compute the real discount rate using the Fisher equation.

    Formula::

        real = (1 + nominal) / (1 + inflation) - 1

    Args:
        nominal_rate: Nominal annual rate as decimal (e.g. 0.05 for 5%).
        inflation_rate: Annual inflation rate as decimal. Defaults to
            ``MOROCCO_INFLATION_RATE``.

    Returns:
        Dict with ``nominal``, ``inflation``, ``real_rate``,
        ``real_rate_pct``, and ``bam_base_rate``.

    Raises:
        ValueError: If inflation_rate equals -1 (division by zero) or
            nominal_rate is negative.
    """
    if nominal_rate < 0:
        raise ValueError(f"nominal_rate must be non-negative, got {nominal_rate}")

    infl = _to_dec(inflation_rate) if inflation_rate is not None else MOROCCO_INFLATION_RATE

    if infl <= Decimal("-1"):
        raise ValueError(
            f"inflation_rate must be > -1, got {inflation_rate}"
        )

    nominal = _to_dec(nominal_rate)
    real = (Decimal("1") + nominal) / (Decimal("1") + infl) - Decimal("1")
    real_pct = _q(real * Decimal("100"))

    logger.info(
        "Fisher equation: nominal=%.3f, inflation=%.3f -> real=%.4f (%.2f%%)",
        float(nominal),
        float(infl),
        float(real),
        float(real_pct),
    )

    return {
        "nominal": float(nominal),
        "inflation": float(infl),
        "real_rate": float(_q(real)),
        "real_rate_pct": float(real_pct),
        "bam_base_rate": float(BAM_BASE_RATE),
    }


# ---------------------------------------------------------------------------
# ONEE tariff accessor
# ---------------------------------------------------------------------------


def get_onee_tariff(period: str | None = None) -> dict:
    """Get ONEE electricity tariff schedule.

    Args:
        period: Specific tariff period (``creuse``, ``pleine``, ``pointe``).
            If ``None``, returns the full schedule plus the blended rate.

    Returns:
        If *period* is specified: dict with ``period``, ``rate_mad_kwh``,
        ``hours``, ``description``.

        If *period* is ``None``: dict with ``schedule`` (full tariff table),
        ``blended_rate_mad_kwh``, ``demand_charge_mad_kva``, and
        ``currency``.

    Raises:
        ValueError: If *period* is not a valid tariff key.
    """
    if period is not None:
        key = period.lower().strip()
        if key not in ONEE_TARIFF_SCHEDULE:
            raise ValueError(
                f"Unknown ONEE tariff period '{period}'. "
                f"Valid values: {list(ONEE_TARIFF_SCHEDULE.keys())}"
            )
        entry = ONEE_TARIFF_SCHEDULE[key]
        return {
            "period": key,
            "rate_mad_kwh": float(entry["rate_mad_kwh"]),
            "hours": entry["hours"],
            "description": entry["description"],
            "currency": "MAD",
        }

    # Return full schedule
    schedule = []
    for key, entry in ONEE_TARIFF_SCHEDULE.items():
        schedule.append({
            "period": key,
            "rate_mad_kwh": float(entry["rate_mad_kwh"]),
            "hours": entry["hours"],
            "description": entry["description"],
        })

    return {
        "schedule": schedule,
        "blended_rate_mad_kwh": float(ONEE_BLENDED_RATE),
        "demand_charge_mad_kva": float(ONEE_DEMAND_CHARGE_MAD_KVA),
        "currency": "MAD",
    }


# ---------------------------------------------------------------------------
# Full financial parameter calibration
# ---------------------------------------------------------------------------


def calibrate_financial_params(
    base_year: int = 2026,
    projection_years: int = 15,
    currency: str = "MAD",
) -> dict:
    """Calibrate all financial parameters for SOTREG analysis.

    Aggregates exchange rates, macroeconomic parameters, ONEE tariff
    data, and computed discount rates into a single configuration dict
    suitable for NPV/TCO/IRR calculations.

    Args:
        base_year: The reference year for calibration (default 2026).
        projection_years: Horizon for inflation-adjusted rate series
            (default 15 years, matching CDC 15-year TCO).
        currency: Base currency code (default ``"MAD"``).

    Returns:
        Dict with the following keys:

        - ``base_year`` -- reference year
        - ``projection_years`` -- number of years projected
        - ``currency`` -- base currency code
        - ``exchange_rates`` -- BAM reference rates (EUR/USD/GBP to MAD)
        - ``inflation_rate`` -- HCP Morocco annual inflation rate
        - ``bam_base_rate`` -- Bank Al-Maghrib policy rate
        - ``nominal_discount_rate`` -- BAM base rate (used as nominal)
        - ``real_discount_rate`` -- Fisher-adjusted rate
        - ``onee_tariffs`` -- full ONEE electricity tariff schedule
        - ``inflation_adjusted_rates`` -- year-by-year blended ONEE rate
          adjusted for energy price inflation (3% assumed)

    Raises:
        ValueError: If *base_year* or *projection_years* are invalid.
    """
    if base_year < 2000 or base_year > 2100:
        raise ValueError(f"base_year must be between 2000 and 2100, got {base_year}")
    if projection_years < 1 or projection_years > 50:
        raise ValueError(
            f"projection_years must be between 1 and 50, got {projection_years}"
        )

    # Exchange rates
    exchange_rates = {k: float(v) for k, v in EXCHANGE_RATES.items()}

    # Real discount rate via Fisher equation
    real_rate_result = compute_real_discount_rate(
        nominal_rate=float(BAM_BASE_RATE),
        inflation_rate=float(MOROCCO_INFLATION_RATE),
    )

    # ONEE tariffs
    onee_result = get_onee_tariff()

    # Year-by-year inflation-adjusted ONEE blended rate
    # Energy price escalation assumed at 3% (slightly above general inflation)
    energy_escalation = Decimal("0.03")
    inflation_adjusted_rates: list[dict] = []
    for year_offset in range(projection_years):
        year = base_year + year_offset
        factor = (Decimal("1") + energy_escalation) ** year_offset
        adjusted_rate = _q(ONEE_BLENDED_RATE * factor)
        inflation_adjusted_rates.append({
            "year": year,
            "blended_rate_mad_kwh": float(adjusted_rate),
            "escalation_factor": float(_q(factor)),
        })

    logger.info(
        "Financial calibration complete: base_year=%d, %d-year horizon, "
        "inflation=%.1f%%, real_discount=%.2f%%, blended_onee=%s MAD/kWh",
        base_year,
        projection_years,
        float(MOROCCO_INFLATION_RATE * 100),
        real_rate_result["real_rate_pct"],
        ONEE_BLENDED_RATE,
    )

    return {
        "base_year": base_year,
        "projection_years": projection_years,
        "currency": currency,
        "exchange_rates": exchange_rates,
        "inflation_rate": float(MOROCCO_INFLATION_RATE),
        "bam_base_rate": float(BAM_BASE_RATE),
        "nominal_discount_rate": float(BAM_BASE_RATE),
        "real_discount_rate": real_rate_result["real_rate"],
        "real_discount_rate_pct": real_rate_result["real_rate_pct"],
        "onee_tariffs": onee_result,
        "inflation_adjusted_rates": inflation_adjusted_rates,
        "calibration_date": date.today().isoformat(),
    }
