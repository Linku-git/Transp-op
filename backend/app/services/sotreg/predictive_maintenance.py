from __future__ import annotations

import logging

import numpy as np
from sklearn.ensemble import IsolationForest

from app.services.sotreg.feature_extraction import (
    build_feature_matrix,
    extract_rolling_features,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

CONTAMINATION: float = 0.05
N_ESTIMATORS: int = 200
RANDOM_STATE: int = 42
MIN_TRAINING_SAMPLES: int = 10

SEVERITY_THRESHOLDS: dict[str, float] = {
    "critical": 0.7,
    "medium": 0.4,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_severity(score: float) -> str:
    """Classify anomaly severity based on normalized score.

    Args:
        score: Normalized anomaly score in [0, 1] where 1 = most anomalous.

    Returns:
        Severity string: ``"critical"``, ``"medium"``, or ``"normal"``.
    """
    if score >= SEVERITY_THRESHOLDS["critical"]:
        return "critical"
    if score >= SEVERITY_THRESHOLDS["medium"]:
        return "medium"
    return "normal"


def _normalize_decision_scores(raw_scores: np.ndarray) -> np.ndarray:
    """Normalize IsolationForest decision_function scores to [0, 1].

    IsolationForest's ``decision_function`` returns negative values for
    anomalies and positive values for normal instances. We invert and
    scale so that 1.0 = most anomalous and 0.0 = most normal.

    Args:
        raw_scores: 1D array of raw decision function values.

    Returns:
        1D array of normalized scores in [0, 1].
    """
    # Negate so anomalies become positive
    negated = -raw_scores

    score_min = float(np.min(negated))
    score_max = float(np.max(negated))
    score_range = score_max - score_min

    if score_range < 1e-12:
        # All scores are identical -- return 0.5 as neutral
        return np.full_like(negated, 0.5)

    normalized = (negated - score_min) / score_range
    return normalized


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_isolation_forest(
    feature_matrix: np.ndarray,
    contamination: float = CONTAMINATION,
    n_estimators: int = N_ESTIMATORS,
) -> dict:
    """Train an IsolationForest anomaly detection model.

    Args:
        feature_matrix: 2D numpy array of shape
            ``(n_samples, n_features)``. Must have at least
            ``MIN_TRAINING_SAMPLES`` rows.
        contamination: Expected proportion of anomalies in the data.
            Must be in ``(0, 0.5]``.
        n_estimators: Number of base estimators (isolation trees).

    Returns:
        Dict with keys:
        - ``model`` (IsolationForest): The trained model instance.
        - ``training_samples`` (int): Number of training samples.
        - ``feature_count`` (int): Number of features.

    Raises:
        ValueError: If the feature matrix has fewer than
            ``MIN_TRAINING_SAMPLES`` rows, zero features, or if
            *contamination* is outside the valid range.
    """
    if feature_matrix.ndim != 2:
        raise ValueError(
            f"feature_matrix must be 2D, got {feature_matrix.ndim}D"
        )

    n_samples, n_features = feature_matrix.shape

    if n_samples < MIN_TRAINING_SAMPLES:
        raise ValueError(
            f"Insufficient training data: {n_samples} samples provided, "
            f"minimum required is {MIN_TRAINING_SAMPLES}"
        )

    if n_features == 0:
        raise ValueError("feature_matrix must have at least 1 feature column")

    if not (0 < contamination <= 0.5):
        raise ValueError(
            f"contamination must be in (0, 0.5], got {contamination}"
        )

    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(feature_matrix)

    logger.info(
        "IsolationForest trained: %d samples, %d features, "
        "n_estimators=%d, contamination=%.3f",
        n_samples,
        n_features,
        n_estimators,
        contamination,
    )

    return {
        "model": model,
        "training_samples": n_samples,
        "feature_count": n_features,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_vehicles(
    model: IsolationForest,
    feature_matrix: np.ndarray,
    vehicle_ids: list[str],
) -> list[dict]:
    """Score vehicles for anomalous behaviour using a trained model.

    IsolationForest's ``decision_function`` returns negative values for
    anomalies. We normalize to a 0-1 scale where 1 = most anomalous,
    then classify severity as:

    - ``score >= 0.7``: **critical**
    - ``score >= 0.4``: **medium**
    - ``score < 0.4``: **normal**

    Args:
        model: Trained IsolationForest instance.
        feature_matrix: 2D array of shape ``(n_vehicles, n_features)``.
        vehicle_ids: List of vehicle identifier strings, matching the
            row order of *feature_matrix*.

    Returns:
        List of dicts, one per vehicle, each with:
        - ``vehicle_id`` (str)
        - ``anomaly_score`` (float): Normalized score in [0, 1].
        - ``severity`` (str): ``"critical"``, ``"medium"``, or ``"normal"``.
        - ``is_anomalous`` (bool): True if severity is not ``"normal"``.

    Raises:
        ValueError: If *vehicle_ids* length does not match
            *feature_matrix* rows.
    """
    if feature_matrix.ndim != 2:
        raise ValueError(
            f"feature_matrix must be 2D, got {feature_matrix.ndim}D"
        )

    n_vehicles = feature_matrix.shape[0]

    if len(vehicle_ids) != n_vehicles:
        raise ValueError(
            f"vehicle_ids length ({len(vehicle_ids)}) does not match "
            f"feature_matrix rows ({n_vehicles})"
        )

    if n_vehicles == 0:
        logger.info("Empty feature matrix provided, returning empty scores")
        return []

    # Get raw decision function scores
    raw_scores = model.decision_function(feature_matrix)
    normalized = _normalize_decision_scores(raw_scores)

    results: list[dict] = []
    for idx in range(n_vehicles):
        score = round(float(normalized[idx]), 4)
        severity = _classify_severity(score)
        results.append({
            "vehicle_id": vehicle_ids[idx],
            "anomaly_score": score,
            "severity": severity,
            "is_anomalous": severity != "normal",
        })

    n_anomalous = sum(1 for r in results if r["is_anomalous"])
    logger.info(
        "Scored %d vehicles: %d anomalous (%.1f%%)",
        n_vehicles,
        n_anomalous,
        n_anomalous / n_vehicles * 100 if n_vehicles else 0,
    )

    return results


# ---------------------------------------------------------------------------
# Alert generation
# ---------------------------------------------------------------------------

def generate_maintenance_alerts(
    scores: list[dict],
    features: dict | None = None,
) -> list[dict]:
    """Generate maintenance alerts for vehicles with anomalous scores.

    Only vehicles with ``severity`` of ``"medium"`` or ``"critical"`` produce
    alerts. Normal vehicles are skipped.

    Args:
        scores: List of vehicle score dicts as returned by
            ``score_vehicles``.
        features: Optional dict mapping vehicle_id to its feature dict
            (e.g. from ``extract_rolling_features``). If provided, the
            alert includes the feature breakdown.

    Returns:
        List of alert dicts, each with:
        - ``vehicle_id`` (str)
        - ``alert_type`` (str): ``"predictive_maintenance"``
        - ``severity`` (str): ``"critical"`` or ``"medium"``
        - ``anomaly_score`` (float)
        - ``message`` (str): Human-readable alert description.
        - ``features`` (dict | None): Feature breakdown if available.
    """
    if not scores:
        return []

    alerts: list[dict] = []

    for score_entry in scores:
        severity = score_entry.get("severity", "normal")
        if severity == "normal":
            continue

        vehicle_id = score_entry["vehicle_id"]
        anomaly_score = score_entry["anomaly_score"]

        # Build descriptive message
        if severity == "critical":
            message = (
                f"Vehicle {vehicle_id} shows critical anomaly patterns "
                f"(score: {anomaly_score:.2f}). Immediate inspection "
                f"recommended."
            )
        else:
            message = (
                f"Vehicle {vehicle_id} shows moderate anomaly patterns "
                f"(score: {anomaly_score:.2f}). Schedule preventive "
                f"maintenance."
            )

        # Attach features if available
        vehicle_features = None
        if features is not None:
            vehicle_features = features.get(vehicle_id)

        alerts.append({
            "vehicle_id": vehicle_id,
            "alert_type": "predictive_maintenance",
            "severity": severity,
            "anomaly_score": anomaly_score,
            "message": message,
            "features": vehicle_features,
        })

    logger.info(
        "Generated %d maintenance alerts from %d scored vehicles "
        "(critical=%d, medium=%d)",
        len(alerts),
        len(scores),
        sum(1 for a in alerts if a["severity"] == "critical"),
        sum(1 for a in alerts if a["severity"] == "medium"),
    )

    return alerts


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_predictive_pipeline(
    readings: list[dict],
) -> dict:
    """Run the full predictive maintenance pipeline.

    Steps:
    1. Group readings by vehicle_id.
    2. Extract rolling features per vehicle.
    3. Build a feature matrix.
    4. Train an IsolationForest model.
    5. Score all vehicles.
    6. Generate maintenance alerts.

    Edge cases handled:
    - Empty readings: returns empty results.
    - Single vehicle: returns scores but model quality is low.
    - Fewer than ``MIN_TRAINING_SAMPLES`` vehicles: returns an error
      indicator instead of training.

    Args:
        readings: List of telemetry reading dicts, each with
            ``vehicle_id``, ``timestamp``, ``sensor_type``, ``value``.

    Returns:
        Dict with keys:
        - ``alerts`` (list[dict]): Maintenance alerts for anomalous
          vehicles.
        - ``scores`` (list[dict]): Anomaly scores for all vehicles.
        - ``model_info`` (dict): Training metadata or error info.
        - ``vehicles_processed`` (int): Number of vehicles analyzed.
    """
    if not readings:
        logger.info("No readings provided to predictive pipeline")
        return {
            "alerts": [],
            "scores": [],
            "model_info": {
                "status": "skipped",
                "reason": "no readings provided",
            },
            "vehicles_processed": 0,
        }

    # Step 1: Group readings by vehicle_id
    vehicle_readings: dict[str, list[dict]] = {}
    for r in readings:
        vid = str(r.get("vehicle_id", "unknown"))
        if vid not in vehicle_readings:
            vehicle_readings[vid] = []
        vehicle_readings[vid].append(r)

    logger.info(
        "Pipeline: %d total readings across %d vehicles",
        len(readings),
        len(vehicle_readings),
    )

    # Step 2: Extract features per vehicle
    vehicle_feature_list: list[dict] = []
    features_by_vehicle: dict[str, dict] = {}

    for vid, v_readings in vehicle_readings.items():
        vf = extract_rolling_features(v_readings)
        vehicle_feature_list.append(vf)
        features_by_vehicle[vid] = vf.get("features", {})

    # Step 3: Build feature matrix
    try:
        matrix_result = build_feature_matrix(vehicle_feature_list)
    except ValueError as exc:
        logger.warning("Failed to build feature matrix: %s", exc)
        return {
            "alerts": [],
            "scores": [],
            "model_info": {
                "status": "error",
                "reason": str(exc),
            },
            "vehicles_processed": len(vehicle_readings),
        }

    feature_matrix = matrix_result["matrix"]
    vehicle_ids = matrix_result["vehicle_ids"]
    feature_names = matrix_result["feature_names"]

    n_vehicles = feature_matrix.shape[0]

    # Step 4: Train model (requires minimum samples)
    if n_vehicles < MIN_TRAINING_SAMPLES:
        logger.warning(
            "Insufficient vehicles for training: %d < %d minimum. "
            "Returning empty results.",
            n_vehicles,
            MIN_TRAINING_SAMPLES,
        )
        return {
            "alerts": [],
            "scores": [],
            "model_info": {
                "status": "insufficient_data",
                "reason": (
                    f"Need at least {MIN_TRAINING_SAMPLES} vehicles, "
                    f"got {n_vehicles}"
                ),
                "vehicles_available": n_vehicles,
                "minimum_required": MIN_TRAINING_SAMPLES,
            },
            "vehicles_processed": n_vehicles,
        }

    try:
        train_result = train_isolation_forest(feature_matrix)
    except ValueError as exc:
        logger.error("Model training failed: %s", exc)
        return {
            "alerts": [],
            "scores": [],
            "model_info": {
                "status": "error",
                "reason": str(exc),
            },
            "vehicles_processed": n_vehicles,
        }

    model = train_result["model"]

    # Step 5: Score vehicles
    scores = score_vehicles(model, feature_matrix, vehicle_ids)

    # Step 6: Generate alerts
    alerts = generate_maintenance_alerts(scores, features=features_by_vehicle)

    model_info = {
        "status": "success",
        "training_samples": train_result["training_samples"],
        "feature_count": train_result["feature_count"],
        "feature_names": feature_names,
        "contamination": CONTAMINATION,
        "n_estimators": N_ESTIMATORS,
    }

    logger.info(
        "Predictive pipeline complete: %d vehicles, %d alerts "
        "(critical=%d, medium=%d)",
        n_vehicles,
        len(alerts),
        sum(1 for a in alerts if a["severity"] == "critical"),
        sum(1 for a in alerts if a["severity"] == "medium"),
    )

    return {
        "alerts": alerts,
        "scores": scores,
        "model_info": model_info,
        "vehicles_processed": n_vehicles,
    }
