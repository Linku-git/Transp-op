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
# CDC SOTREG v5.0 default weights and criteria configuration
# ---------------------------------------------------------------------------

CDC_DEFAULT_WEIGHTS: dict[str, float] = {
    "capex": 0.20,
    "opex": 0.20,
    "co2": 0.25,
    "risk": 0.15,
    "comfort": 0.10,
    "maturity": 0.10,
}

CRITERIA_DIRECTION: dict[str, str] = {
    "capex": "cost",
    "opex": "cost",
    "co2": "cost",
    "risk": "cost",
    "comfort": "benefit",
    "maturity": "benefit",
}

REQUIRED_CRITERIA: set[str] = set(CDC_DEFAULT_WEIGHTS.keys())


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _validate_weights(weights: dict[str, float]) -> None:
    """Validate that weights contain exactly the 6 criteria and sum to 1.0.

    Raises:
        ValueError: If keys are wrong or weights do not sum to 1.0 (within
            tolerance of 0.001).
    """
    missing = REQUIRED_CRITERIA - set(weights.keys())
    extra = set(weights.keys()) - REQUIRED_CRITERIA
    if missing or extra:
        raise ValueError(
            f"Weights must contain exactly {sorted(REQUIRED_CRITERIA)}. "
            f"Missing: {sorted(missing)}, extra: {sorted(extra)}"
        )

    for k, v in weights.items():
        if v < 0:
            raise ValueError(
                f"Weight for '{k}' must be non-negative, got {v}"
            )

    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.001:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_sum:.6f}"
        )


def _validate_alternatives(alternatives: list[dict]) -> None:
    """Validate that alternatives contain all required criteria fields.

    Raises:
        ValueError: If alternatives is empty or a required field is missing.
    """
    if not alternatives:
        raise ValueError("alternatives must be a non-empty list")

    for i, alt in enumerate(alternatives):
        if "name" not in alt:
            raise ValueError(
                f"Alternative at index {i} is missing 'name' field"
            )
        for criterion in REQUIRED_CRITERIA:
            if criterion not in alt:
                raise ValueError(
                    f"Alternative '{alt.get('name', i)}' is missing "
                    f"criterion '{criterion}'"
                )
            val = alt[criterion]
            if not isinstance(val, (int, float)):
                raise ValueError(
                    f"Alternative '{alt['name']}' criterion '{criterion}' "
                    f"must be numeric, got {type(val).__name__}"
                )


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_value(
    value: float,
    v_min: float,
    v_max: float,
    direction: str,
) -> float:
    """Normalize a criterion value to the 1-5 scale.

    For cost criteria (lower is better)::

        n = 5 - 4 * (value - v_min) / (v_max - v_min)

    So the best (minimum) value maps to 5 and the worst (maximum) to 1.

    For benefit criteria (higher is better)::

        n = 1 + 4 * (value - v_min) / (v_max - v_min)

    So the best (maximum) value maps to 5 and the worst (minimum) to 1.

    When all alternatives have the same value (``v_max == v_min``), the
    normalized score is 3.0 (midpoint).

    Args:
        value: The raw criterion value.
        v_min: Minimum value across all alternatives for this criterion.
        v_max: Maximum value across all alternatives for this criterion.
        direction: ``"cost"`` (lower is better) or ``"benefit"`` (higher is
            better).

    Returns:
        Normalized score in the range [1.0, 5.0].

    Raises:
        ValueError: If *direction* is not ``"cost"`` or ``"benefit"``.
    """
    if direction not in ("cost", "benefit"):
        raise ValueError(
            f"direction must be 'cost' or 'benefit', got '{direction}'"
        )

    if v_max == v_min:
        return 3.0

    ratio = (value - v_min) / (v_max - v_min)

    if direction == "cost":
        return 5.0 - 4.0 * ratio
    else:
        return 1.0 + 4.0 * ratio


# ---------------------------------------------------------------------------
# MCDA weighted sum scoring
# ---------------------------------------------------------------------------


def compute_mcda_scores(
    alternatives: list[dict],
    weights: dict[str, float] | None = None,
) -> dict:
    """Compute MCDA weighted sum scores for transport alternatives.

    Each alternative is scored using::

        S(a) = sum(w_k * n_k(a_k))

    where ``w_k`` is the weight for criterion *k* and ``n_k`` is the
    normalized value (1-5 scale) for alternative *a* on criterion *k*.

    Args:
        alternatives: List of dicts, each with keys ``name``, ``capex``,
            ``opex``, ``co2``, ``risk``, ``comfort``, ``maturity``.
        weights: Dict mapping each criterion to its weight. Must sum to
            1.0. Defaults to ``CDC_DEFAULT_WEIGHTS``.

    Returns:
        Dict containing:
        - ``ranked_alternatives`` -- list sorted by score descending, each
          with ``name``, ``score``, ``normalized_values``, ``rank``
        - ``weights_used`` -- the weights applied
        - ``criteria_ranges`` -- ``{criterion: {min, max}}``
        - ``best_alternative`` -- name of the top-ranked alternative
        - ``worst_alternative`` -- name of the bottom-ranked alternative

    Raises:
        ValueError: If alternatives is empty, weights are invalid, or
            required fields are missing.
    """
    _validate_alternatives(alternatives)

    if weights is None:
        weights = dict(CDC_DEFAULT_WEIGHTS)
    _validate_weights(weights)

    # ---- Compute min/max per criterion -----------------------------------
    criteria_ranges: dict[str, dict[str, float]] = {}
    for criterion in REQUIRED_CRITERIA:
        values = [alt[criterion] for alt in alternatives]
        criteria_ranges[criterion] = {
            "min": min(values),
            "max": max(values),
        }

    # ---- Normalize and score each alternative ----------------------------
    scored: list[dict] = []
    for alt in alternatives:
        normalized_values: dict[str, float] = {}
        weighted_score = Decimal("0")

        for criterion in sorted(REQUIRED_CRITERIA):
            cr = criteria_ranges[criterion]
            direction = CRITERIA_DIRECTION[criterion]
            n_val = normalize_value(
                alt[criterion], cr["min"], cr["max"], direction,
            )
            normalized_values[criterion] = float(
                _q(_to_dec(n_val))
            )
            weighted_score += _to_dec(weights[criterion]) * _to_dec(n_val)

        scored.append({
            "name": alt["name"],
            "score": float(_q(weighted_score)),
            "normalized_values": normalized_values,
        })

    # ---- Sort by score descending, assign ranks --------------------------
    scored.sort(key=lambda x: x["score"], reverse=True)
    for rank, item in enumerate(scored, start=1):
        item["rank"] = rank

    best = scored[0]["name"]
    worst = scored[-1]["name"]

    logger.info(
        "MCDA scoring complete: %d alternatives, best=%s (%.2f), "
        "worst=%s (%.2f)",
        len(scored),
        best,
        scored[0]["score"],
        worst,
        scored[-1]["score"],
    )

    return {
        "ranked_alternatives": scored,
        "weights_used": weights,
        "criteria_ranges": criteria_ranges,
        "best_alternative": best,
        "worst_alternative": worst,
    }


# ---------------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------------


def _redistribute_weights(
    base_weights: dict[str, float],
    target_criterion: str,
    new_weight: float,
) -> dict[str, float]:
    """Redistribute weight change proportionally across other criteria.

    When *target_criterion* weight changes by delta, the remaining criteria
    absorb the opposite delta proportionally to their original weights so
    that the total remains 1.0.

    Args:
        base_weights: Original weights dict.
        target_criterion: The criterion whose weight is being changed.
        new_weight: The new weight for the target criterion.

    Returns:
        New weights dict summing to 1.0.
    """
    delta = new_weight - base_weights[target_criterion]
    others_sum = sum(
        w for k, w in base_weights.items() if k != target_criterion
    )

    new_weights: dict[str, float] = {}
    for k, w in base_weights.items():
        if k == target_criterion:
            new_weights[k] = new_weight
        elif others_sum > 0:
            new_weights[k] = w - delta * (w / others_sum)
        else:
            # Edge case: all other weights are 0
            remaining_count = len(base_weights) - 1
            new_weights[k] = (1.0 - new_weight) / remaining_count

    # Clamp to non-negative and re-normalize to handle floating point drift
    for k in new_weights:
        if new_weights[k] < 0:
            new_weights[k] = 0.0

    total = sum(new_weights.values())
    if total > 0:
        for k in new_weights:
            new_weights[k] = new_weights[k] / total

    return new_weights


def compute_sensitivity_analysis(
    alternatives: list[dict],
    weights: dict[str, float] | None = None,
    delta_pct: float = 20.0,
) -> dict:
    """Perform sensitivity analysis by varying each weight +/- delta_pct%.

    For each criterion, the weight is increased and decreased by
    *delta_pct* percent of its original value. The delta is
    redistributed proportionally across the other criteria so that the
    total weight remains 1.0. The MCDA scoring is recomputed for each
    perturbation and the ranking is compared to the base case.

    Args:
        alternatives: List of alternative dicts (same format as
            :func:`compute_mcda_scores`).
        weights: Base weights. Defaults to ``CDC_DEFAULT_WEIGHTS``.
        delta_pct: Perturbation magnitude in percent (default 20%).

    Returns:
        Dict containing:
        - ``base_ranking`` -- list of ``{name, score, rank}`` from base case
        - ``sensitivity_results`` -- list of per-criterion results with
          ``criterion``, ``weight_original``, ``weight_plus``,
          ``weight_minus``, ``ranking_plus``, ``ranking_minus``,
          ``ranking_changed``, ``is_critical``
        - ``critical_criteria`` -- list of criteria that cause ranking change
        - ``stability_score`` -- 0-100 (% of perturbations that preserve
          the base ranking)

    Raises:
        ValueError: If alternatives or weights are invalid, or delta_pct
            is non-positive.
    """
    if delta_pct <= 0:
        raise ValueError(
            f"delta_pct must be positive, got {delta_pct}"
        )

    if weights is None:
        weights = dict(CDC_DEFAULT_WEIGHTS)
    _validate_weights(weights)
    _validate_alternatives(alternatives)

    # ---- Base case -------------------------------------------------------
    base_result = compute_mcda_scores(alternatives, weights)
    base_ranking = [
        {"name": a["name"], "score": a["score"], "rank": a["rank"]}
        for a in base_result["ranked_alternatives"]
    ]
    base_order = [a["name"] for a in base_ranking]

    # ---- Perturbations ---------------------------------------------------
    sensitivity_results: list[dict] = []
    total_perturbations = 0
    ranking_preserved = 0

    for criterion in sorted(REQUIRED_CRITERIA):
        w_orig = weights[criterion]
        delta = w_orig * (delta_pct / 100.0)

        # Plus perturbation
        w_plus = min(w_orig + delta, 1.0)
        weights_plus = _redistribute_weights(weights, criterion, w_plus)
        result_plus = compute_mcda_scores(alternatives, weights_plus)
        ranking_plus = [
            {"name": a["name"], "score": a["score"], "rank": a["rank"]}
            for a in result_plus["ranked_alternatives"]
        ]
        order_plus = [a["name"] for a in ranking_plus]

        # Minus perturbation
        w_minus = max(w_orig - delta, 0.0)
        weights_minus = _redistribute_weights(weights, criterion, w_minus)
        result_minus = compute_mcda_scores(alternatives, weights_minus)
        ranking_minus = [
            {"name": a["name"], "score": a["score"], "rank": a["rank"]}
            for a in result_minus["ranked_alternatives"]
        ]
        order_minus = [a["name"] for a in ranking_minus]

        # Check if ranking changed
        plus_changed = order_plus != base_order
        minus_changed = order_minus != base_order
        ranking_changed = plus_changed or minus_changed

        total_perturbations += 2
        if not plus_changed:
            ranking_preserved += 1
        if not minus_changed:
            ranking_preserved += 1

        sensitivity_results.append({
            "criterion": criterion,
            "weight_original": float(_q(_to_dec(w_orig))),
            "weight_plus": float(_q(_to_dec(w_plus))),
            "weight_minus": float(_q(_to_dec(w_minus))),
            "ranking_plus": ranking_plus,
            "ranking_minus": ranking_minus,
            "ranking_changed": ranking_changed,
            "is_critical": ranking_changed,
        })

    critical_criteria = [
        r["criterion"] for r in sensitivity_results if r["is_critical"]
    ]

    stability_score = (
        round(100.0 * ranking_preserved / total_perturbations, 1)
        if total_perturbations > 0
        else 100.0
    )

    logger.info(
        "Sensitivity analysis complete: %d criteria, "
        "stability=%.1f%%, critical=%s",
        len(sensitivity_results),
        stability_score,
        critical_criteria or "none",
    )

    return {
        "base_ranking": base_ranking,
        "sensitivity_results": sensitivity_results,
        "critical_criteria": critical_criteria,
        "stability_score": stability_score,
    }


# ---------------------------------------------------------------------------
# McFadden multinomial logit
# ---------------------------------------------------------------------------


def compute_mcfadden_logit(
    alternatives: list[dict],
    beta_cost: float = -0.001,
    beta_time: float = -0.05,
    beta_comfort: float = 0.5,
) -> dict:
    """Compute McFadden multinomial logit choice probabilities.

    The deterministic utility for each alternative *i* is::

        V_i = beta_cost * cost_i + beta_time * time_i + beta_comfort * comfort_i

    The choice probability follows the logit formula::

        P(i) = exp(V_i) / sum_j(exp(V_j))

    To avoid numerical overflow, utilities are shifted by subtracting the
    maximum utility before exponentiation (log-sum-exp trick).

    Args:
        alternatives: List of dicts, each with ``name``, ``cost``,
            ``time_minutes``, ``comfort``.
        beta_cost: Coefficient for cost (typically negative).
        beta_time: Coefficient for travel time in minutes (typically
            negative).
        beta_comfort: Coefficient for comfort index (typically positive).

    Returns:
        Dict containing:
        - ``probabilities`` -- list of ``{name, utility, probability}``
          sorted by probability descending
        - ``probabilities_sum`` -- sanity check (should be ~1.0)
        - ``dominant_mode`` -- name with highest probability

    Raises:
        ValueError: If alternatives is empty or required fields are missing.
    """
    if not alternatives:
        raise ValueError("alternatives must be a non-empty list")

    # ---- Validate fields -------------------------------------------------
    required_fields = {"name", "cost", "time_minutes", "comfort"}
    for i, alt in enumerate(alternatives):
        missing = required_fields - set(alt.keys())
        if missing:
            raise ValueError(
                f"Alternative at index {i} is missing fields: "
                f"{sorted(missing)}"
            )

    # ---- Compute utilities -----------------------------------------------
    utilities: list[tuple[str, float]] = []
    for alt in alternatives:
        v = (
            beta_cost * alt["cost"]
            + beta_time * alt["time_minutes"]
            + beta_comfort * alt["comfort"]
        )
        utilities.append((alt["name"], v))

    # ---- Log-sum-exp trick for numerical stability -----------------------
    v_max = max(v for _, v in utilities)
    exp_values = [(name, v, math.exp(v - v_max)) for name, v in utilities]
    exp_sum = sum(ev for _, _, ev in exp_values)

    # ---- Probabilities ---------------------------------------------------
    probabilities: list[dict] = []
    for name, v, ev in exp_values:
        p = ev / exp_sum if exp_sum > 0 else 1.0 / len(alternatives)
        probabilities.append({
            "name": name,
            "utility": float(_q(_to_dec(v))),
            "probability": float(
                _q(_to_dec(p))
            ),
        })

    probabilities.sort(key=lambda x: x["probability"], reverse=True)
    prob_sum = sum(p["probability"] for p in probabilities)
    dominant = probabilities[0]["name"]

    logger.info(
        "McFadden logit: %d alternatives, dominant=%s (P=%.2f), "
        "sum=%.4f",
        len(probabilities),
        dominant,
        probabilities[0]["probability"],
        prob_sum,
    )

    return {
        "probabilities": probabilities,
        "probabilities_sum": float(_q(_to_dec(prob_sum))),
        "dominant_mode": dominant,
    }
