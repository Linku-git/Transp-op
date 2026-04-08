from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default weights for risk scoring formula
DEFAULT_WEIGHTS = {
    "isolation": 0.25,
    "lighting": 0.20,
    "tc_frequency": 0.20,
    "night_risk": 0.20,
    "employee_perception": 0.15,
}

# Default threshold above which a stop is flagged as critical
DEFAULT_CRITICAL_THRESHOLD = 0.7


@dataclass
class RiskWeights:
    isolation: float = 0.25
    lighting: float = 0.20
    tc_frequency: float = 0.20
    night_risk: float = 0.20
    employee_perception: float = 0.15


def compute_risk_score(
    isolation_score: float,
    lighting_score: float,
    tc_frequency_score: float,
    night_risk_multiplier: float,
    employee_perception_avg: float,
    weights: RiskWeights | None = None,
    is_night: bool = False,
) -> float:
    """
    Compute composite risk score using weighted formula:
    Risk = w1*Isolation + w2*(1-Lighting) + w3*(1-TC_Frequency)
         + w4*Night_Flag + w5*(1-Employee_Perception)

    All factor scores are 0-1 where 1 = highest risk.
    Lighting, TC frequency, and employee perception are inverted
    because higher values mean SAFER.
    """
    w = weights or RiskWeights()

    night_factor = night_risk_multiplier if is_night else 0.0

    score = (
        w.isolation * _clamp(isolation_score)
        + w.lighting * (1.0 - _clamp(lighting_score))
        + w.tc_frequency * (1.0 - _clamp(tc_frequency_score))
        + w.night_risk * _clamp(night_factor)
        + w.employee_perception * (1.0 - _clamp(employee_perception_avg))
    )

    return round(_clamp(score), 4)


def is_critical(
    composite_score: float,
    threshold: float = DEFAULT_CRITICAL_THRESHOLD,
) -> bool:
    """Check if a stop's composite risk score exceeds the critical threshold."""
    return composite_score >= threshold


def compute_and_flag(
    isolation_score: float,
    lighting_score: float,
    tc_frequency_score: float,
    night_risk_multiplier: float,
    employee_perception_avg: float,
    weights: RiskWeights | None = None,
    threshold: float = DEFAULT_CRITICAL_THRESHOLD,
) -> tuple[float, bool]:
    """Compute risk score and return (score, is_critical) tuple."""
    # Compute for both day and night, take maximum
    day_score = compute_risk_score(
        isolation_score, lighting_score, tc_frequency_score,
        night_risk_multiplier, employee_perception_avg,
        weights=weights, is_night=False,
    )
    night_score = compute_risk_score(
        isolation_score, lighting_score, tc_frequency_score,
        night_risk_multiplier, employee_perception_avg,
        weights=weights, is_night=True,
    )

    # Use the worst-case (night) score for the composite
    score = max(day_score, night_score)
    critical = is_critical(score, threshold)

    return score, critical


def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to [min_val, max_val] range."""
    return max(min_val, min(max_val, value))
