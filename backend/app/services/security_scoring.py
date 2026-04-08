from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Weights for security score computation
QUESTIONNAIRE_WEIGHT = 0.35
VULNERABLE_STOPS_WEIGHT = 0.25
NIGHT_EXPOSURE_WEIGHT = 0.25
STOP_ISOLATION_WEIGHT = 0.15

# Risk level thresholds (0-100, higher = safer)
RISK_THRESHOLDS = {
    "critical": 25,
    "high": 50,
    "medium": 75,
}

# Night hours
NIGHT_START_HOUR = 20
NIGHT_END_HOUR = 6
NIGHT_END_MINUTE = 30

# Time slots for heatmap
TIME_SLOTS = [
    ("05h-07h", 5, 7, True),
    ("07h-09h", 7, 9, False),
    ("09h-12h", 9, 12, False),
    ("12h-14h", 12, 14, False),
    ("14h-17h", 14, 17, False),
    ("17h-19h", 17, 19, False),
    ("19h-22h", 19, 22, False),
    ("22h-05h", 22, 5, True),
]


def compute_security_score(
    questionnaire_rating: int | None = None,
    vulnerable_stop_count: int = 0,
    night_commute_exposure: float = 0.0,
    avg_stop_isolation: float = 0.0,
) -> tuple[int, str, dict]:
    """
    Compute security score (0-100, higher = safer).

    Factors:
    - questionnaire_rating: 1-5 → 20-100 (35%)
    - vulnerable_stop_count: 0-10+ → 100-0 (25%)
    - night_commute_exposure: 0-1 → 100-0 (25%)
    - avg_stop_isolation: 0-1 → 100-0 (15%)
    """
    # Questionnaire factor (1=20, 5=100)
    q_score = ((questionnaire_rating or 3) / 5.0) * 100.0

    # Vulnerable stops factor (0=100, 10+=0)
    v_score = max(0.0, 100.0 - (vulnerable_stop_count * 10.0))

    # Night exposure factor (0=100, 1=0)
    n_score = (1.0 - min(1.0, night_commute_exposure)) * 100.0

    # Stop isolation factor (0=100, 1=0)
    i_score = (1.0 - min(1.0, avg_stop_isolation)) * 100.0

    # Weighted composite
    composite = (
        QUESTIONNAIRE_WEIGHT * q_score
        + VULNERABLE_STOPS_WEIGHT * v_score
        + NIGHT_EXPOSURE_WEIGHT * n_score
        + STOP_ISOLATION_WEIGHT * i_score
    )

    score = max(0, min(100, round(composite)))
    risk_level = classify_risk_level(score)

    factors = {
        "questionnaire_score": round(q_score, 1),
        "vulnerable_stops_score": round(v_score, 1),
        "night_exposure_score": round(n_score, 1),
        "stop_isolation_score": round(i_score, 1),
        "weights": {
            "questionnaire": QUESTIONNAIRE_WEIGHT,
            "vulnerable_stops": VULNERABLE_STOPS_WEIGHT,
            "night_exposure": NIGHT_EXPOSURE_WEIGHT,
            "stop_isolation": STOP_ISOLATION_WEIGHT,
        },
    }

    return score, risk_level, factors


def classify_risk_level(score: int) -> str:
    """Classify score into risk level (higher score = safer)."""
    if score <= RISK_THRESHOLDS["critical"]:
        return "critical"
    if score <= RISK_THRESHOLDS["high"]:
        return "high"
    if score <= RISK_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def is_night_hour(hour: int, minute: int = 0) -> bool:
    """Check if a given hour is in night mode (20h00-6h30)."""
    if hour >= NIGHT_START_HOUR:
        return True
    if hour < NIGHT_END_HOUR:
        return True
    if hour == NIGHT_END_HOUR and minute <= NIGHT_END_MINUTE:
        return True
    return False


def compute_time_slot_risk(
    slot_label: str,
    start_hour: int,
    end_hour: int,
    is_night: bool,
    base_risk: float = 0.3,
) -> float:
    """Compute risk score for a time slot. Night slots get elevated risk."""
    risk = base_risk
    if is_night:
        risk *= 1.8  # 80% risk elevation for night
    return min(1.0, risk)


def generate_heatmap(base_risk: float = 0.3) -> list[dict]:
    """Generate security heatmap for all time slots."""
    return [
        {
            "time_slot": label,
            "risk_score": round(compute_time_slot_risk(label, start, end, night, base_risk), 2),
            "is_night": night,
        }
        for label, start, end, night in TIME_SLOTS
    ]


def aggregate_scores(
    scores: list[dict],
    group_key: str = "site_id",
) -> list[dict]:
    """Aggregate security scores by group (site, team, shift)."""
    groups: dict[str, list[int]] = {}
    for s in scores:
        key_val = str(s.get(group_key, "unknown"))
        groups.setdefault(key_val, []).append(s.get("score", 0))

    result = []
    for key_val, score_list in groups.items():
        avg = sum(score_list) / len(score_list) if score_list else 0
        risk_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for sc in score_list:
            rl = classify_risk_level(sc)
            risk_dist[rl] += 1

        result.append({
            "group_key": group_key,
            "group_value": key_val,
            "avg_score": round(avg, 1),
            "employee_count": len(score_list),
            "risk_distribution": risk_dist,
        })

    return result
