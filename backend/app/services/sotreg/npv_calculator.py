from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

from scipy.optimize import brentq

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Morocco financial constants
# ---------------------------------------------------------------------------

# Bank Al-Maghrib reference rate (2024-2025 range)
BAM_BASE_RATE = 0.03  # 3% base rate
# Default discount rate for transport infrastructure investment in Morocco
DEFAULT_DISCOUNT_RATE = 0.08  # 8%

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
# NPV (VAN)
# ---------------------------------------------------------------------------


def compute_npv(
    cash_flows: list[float],
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    currency: str = "MAD",
) -> dict:
    """Compute Net Present Value (VAN in French).

    Formula::

        VAN = sum(CF_t / (1 + r)^t)  for t = 0 .. N

    ``cash_flows[0]`` is typically negative (initial investment at t=0,
    not discounted).

    Args:
        cash_flows: List of annual cash flows starting at year 0.
            Must contain at least one element.
        discount_rate: Annual discount rate (e.g. 0.08 for 8%).
            Must be >= 0.
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``npv`` -- the net present value (float)
        - ``discount_rate`` -- the rate used
        - ``cash_flow_count`` -- number of periods
        - ``present_values`` -- list of PV per year
        - ``is_viable`` -- True if npv > 0
        - ``currency``

    Raises:
        ValueError: If *cash_flows* is empty or *discount_rate* is negative.
    """
    if not cash_flows:
        raise ValueError("cash_flows must contain at least one element")
    if discount_rate < 0:
        raise ValueError(
            f"discount_rate must be non-negative, got {discount_rate}"
        )

    r = _to_dec(discount_rate)
    one_plus_r = Decimal("1") + r
    present_values: list[float] = []
    npv_acc = Decimal("0")

    for t, cf in enumerate(cash_flows):
        cf_dec = _to_dec(cf)
        # Year 0 is not discounted; zero rate means no discounting at all
        if t == 0 or r == Decimal("0"):
            discount_factor = Decimal("1")
        else:
            discount_factor = one_plus_r ** t
        pv = _q(cf_dec / discount_factor)

        present_values.append(float(pv))
        npv_acc += pv

    npv_final = _q(npv_acc)

    logger.info(
        "NPV computed: %s %s (rate=%.2f%%, periods=%d, viable=%s)",
        npv_final,
        currency,
        discount_rate * 100,
        len(cash_flows),
        npv_final > 0,
    )

    return {
        "npv": float(npv_final),
        "discount_rate": discount_rate,
        "cash_flow_count": len(cash_flows),
        "present_values": present_values,
        "is_viable": float(npv_final) > 0,
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# IRR (TRI)
# ---------------------------------------------------------------------------


def compute_irr(
    cash_flows: list[float],
) -> dict:
    """Compute Internal Rate of Return using ``scipy.optimize.brentq``.

    IRR is the discount rate *r* at which ``NPV(r) = 0``.  The search
    interval is ``[-0.5, 10.0]`` (from -50 % to 1000 %).

    The function requires at least one sign change in *cash_flows*
    (typically a negative initial investment followed by positive returns).

    Args:
        cash_flows: List of annual cash flows starting at year 0.
            Must contain at least two elements and at least one sign change.

    Returns:
        Dict containing:
        - ``irr`` -- the rate as a float, or ``None`` if not convergent
        - ``irr_pct`` -- the rate as a percentage, or ``None``
        - ``converged`` -- True if a root was found
        - ``npv_at_irr`` -- NPV evaluated at the IRR (should be ~0)

    Raises:
        ValueError: If *cash_flows* has fewer than 2 elements.
    """
    if len(cash_flows) < 2:
        raise ValueError(
            "cash_flows must contain at least 2 elements to compute IRR"
        )

    # Check for sign change -- IRR is only defined if there is one
    has_positive = any(cf > 0 for cf in cash_flows)
    has_negative = any(cf < 0 for cf in cash_flows)
    if not (has_positive and has_negative):
        logger.warning(
            "IRR undefined: cash flows have no sign change "
            "(positive=%s, negative=%s)",
            has_positive,
            has_negative,
        )
        # Still return a valid result structure
        total = sum(cash_flows)
        return {
            "irr": None,
            "irr_pct": None,
            "converged": False,
            "npv_at_irr": total,
        }

    def _npv_at_rate(rate: float) -> float:
        """Evaluate NPV at a given discount rate (float arithmetic)."""
        return sum(cf / (1.0 + rate) ** t for t, cf in enumerate(cash_flows))

    try:
        irr_value = brentq(_npv_at_rate, -0.5, 10.0, xtol=1e-10, maxiter=1000)
        npv_check = _npv_at_rate(irr_value)
        irr_pct = float(_q(_to_dec(irr_value * 100)))

        logger.info(
            "IRR converged: %.4f (%.2f%%), NPV at IRR = %.6f",
            irr_value,
            irr_pct,
            npv_check,
        )

        return {
            "irr": round(irr_value, 6),
            "irr_pct": irr_pct,
            "converged": True,
            "npv_at_irr": round(npv_check, 6),
        }
    except (ValueError, RuntimeError) as exc:
        logger.warning("IRR computation did not converge: %s", exc)
        return {
            "irr": None,
            "irr_pct": None,
            "converged": False,
            "npv_at_irr": _npv_at_rate(0.0),
        }


# ---------------------------------------------------------------------------
# Payback period
# ---------------------------------------------------------------------------


def compute_payback_period(
    cash_flows: list[float],
    currency: str = "MAD",
) -> dict:
    """Compute simple (undiscounted) payback period.

    The payback period is the year at which cumulative cash flow turns
    from negative to positive.  If the transition happens between two
    integer years, linear interpolation is used to obtain a fractional
    year estimate.

    Args:
        cash_flows: List of annual cash flows starting at year 0.
            Must contain at least one element.
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict containing:
        - ``payback_years`` -- float or ``None`` if cumulative CF never
          turns positive
        - ``cumulative_flows`` -- list of cumulative CF per year
        - ``total_investment`` -- absolute value of initial negative flows
        - ``total_return`` -- sum of all positive flows
        - ``currency``

    Raises:
        ValueError: If *cash_flows* is empty.
    """
    if not cash_flows:
        raise ValueError("cash_flows must contain at least one element")

    cumulative = Decimal("0")
    cumulative_flows: list[float] = []
    payback_years: float | None = None

    for cf in cash_flows:
        cumulative += _to_dec(cf)
        cumulative_flows.append(float(_q(cumulative)))

    # Calculate total investment (sum of leading negative flows)
    total_investment = Decimal("0")
    for cf in cash_flows:
        if cf < 0:
            total_investment += abs(_to_dec(cf))
        else:
            break  # stop at first non-negative flow

    # Calculate total positive returns
    total_return = Decimal("0")
    for cf in cash_flows:
        if cf > 0:
            total_return += _to_dec(cf)

    # Find payback year with linear interpolation
    cum = Decimal("0")
    for t, cf in enumerate(cash_flows):
        prev_cum = cum
        cum += _to_dec(cf)
        if cum >= 0 and prev_cum < 0:
            # Interpolate: fraction of year = |prev_cum| / cf
            cf_dec = _to_dec(cf)
            if cf_dec > 0:
                fraction = float(_q(abs(prev_cum) / cf_dec))
                payback_years = float(_q(_to_dec(t) + _to_dec(fraction)))
            else:
                payback_years = float(t)
            break

    # Special case: if cumulative is non-negative from the start
    if payback_years is None and cumulative_flows and cumulative_flows[0] >= 0:
        payback_years = 0.0

    if payback_years is not None:
        logger.info(
            "Payback period: %.2f years (investment=%s %s, return=%s %s)",
            payback_years,
            _q(total_investment),
            currency,
            _q(total_return),
            currency,
        )
    else:
        logger.warning(
            "Payback period: never reached (investment=%s %s, return=%s %s)",
            _q(total_investment),
            currency,
            _q(total_return),
            currency,
        )

    return {
        "payback_years": payback_years,
        "cumulative_flows": cumulative_flows,
        "total_investment": float(_q(total_investment)),
        "total_return": float(_q(total_return)),
        "currency": currency,
    }


# ---------------------------------------------------------------------------
# Full investment analysis
# ---------------------------------------------------------------------------


def compute_full_investment_analysis(
    cash_flows: list[float],
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    currency: str = "MAD",
) -> dict:
    """Run a full investment analysis combining NPV, IRR, and payback.

    This is a convenience function that calls :func:`compute_npv`,
    :func:`compute_irr`, and :func:`compute_payback_period` and merges
    their results into a single response dict.

    Args:
        cash_flows: List of annual cash flows starting at year 0.
        discount_rate: Annual discount rate for NPV (default 8 %).
        currency: Currency code (default ``"MAD"``).

    Returns:
        Dict with keys ``npv``, ``irr``, ``payback``, plus a top-level
        ``recommendation`` string summarising viability.

    Raises:
        ValueError: If *cash_flows* is empty.
    """
    if not cash_flows:
        raise ValueError("cash_flows must contain at least one element")

    npv_result = compute_npv(cash_flows, discount_rate, currency)
    irr_result = compute_irr(cash_flows) if len(cash_flows) >= 2 else {
        "irr": None,
        "irr_pct": None,
        "converged": False,
        "npv_at_irr": cash_flows[0] if cash_flows else 0.0,
    }
    payback_result = compute_payback_period(cash_flows, currency)

    # Build recommendation
    is_npv_positive = npv_result["is_viable"]
    irr_above_hurdle = (
        irr_result["irr"] is not None
        and irr_result["irr"] > discount_rate
    )
    has_payback = payback_result["payback_years"] is not None

    if is_npv_positive and irr_above_hurdle and has_payback:
        recommendation = "INVEST"
    elif is_npv_positive and has_payback:
        recommendation = "CONSIDER"
    elif is_npv_positive:
        recommendation = "MARGINAL"
    else:
        recommendation = "REJECT"

    logger.info(
        "Full investment analysis: recommendation=%s "
        "(NPV=%s, IRR=%s%%, payback=%s years)",
        recommendation,
        npv_result["npv"],
        irr_result.get("irr_pct"),
        payback_result["payback_years"],
    )

    return {
        "npv": npv_result,
        "irr": irr_result,
        "payback": payback_result,
        "recommendation": recommendation,
        "discount_rate": discount_rate,
        "cash_flow_count": len(cash_flows),
        "currency": currency,
    }
