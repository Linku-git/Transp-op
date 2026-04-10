from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rolling window configuration
# ---------------------------------------------------------------------------

WINDOW_CONFIGS: list[dict[str, int | str]] = [
    {"name": "1h", "seconds": 3600},
    {"name": "24h", "seconds": 86400},
    {"name": "7d", "seconds": 604800},
]

# Minimum readings required per window to compute meaningful statistics
MIN_READINGS_PER_WINDOW = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_timestamp(ts: str | datetime) -> datetime:
    """Parse a timestamp to a timezone-aware datetime.

    Args:
        ts: ISO 8601 string or datetime object.

    Returns:
        Timezone-aware datetime (UTC if naive).
    """
    if isinstance(ts, str):
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    else:
        dt = ts

    # Ensure timezone-aware (assume UTC if naive)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def _compute_stats(values: list[float]) -> dict[str, float]:
    """Compute descriptive statistics for a list of values.

    Args:
        values: Non-empty list of numeric values.

    Returns:
        Dict with ``mean``, ``std``, ``max``, ``min``, ``count``.
    """
    arr = np.array(values, dtype=np.float64)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=0)),
        "max": float(np.max(arr)),
        "min": float(np.min(arr)),
        "count": len(values),
    }


# ---------------------------------------------------------------------------
# Rolling feature extraction
# ---------------------------------------------------------------------------

def extract_rolling_features(
    readings: list[dict],
    reference_time: datetime | None = None,
) -> dict:
    """Extract rolling statistical features from telemetry readings.

    For each unique ``sensor_type`` found in *readings* and for each
    configured time window (1h, 24h, 7d), compute descriptive statistics
    (mean, std, max, min, count) on the values that fall within the window
    ending at *reference_time*.

    Feature naming convention::

        {sensor_type}_{window_name}_{stat}

    For example: ``vibration_1h_mean``, ``temperature_24h_std``.

    If a window has fewer than ``MIN_READINGS_PER_WINDOW`` readings for a
    sensor type, the corresponding features are filled with ``0.0`` (and
    count set to ``0``).

    Args:
        readings: List of reading dicts, each containing at minimum
            ``vehicle_id``, ``timestamp``, ``sensor_type``, ``value``.
        reference_time: The point in time from which windows are computed
            backward. Defaults to ``datetime.now(UTC)`` if not provided.

    Returns:
        Dict with keys:
        - ``vehicle_id`` (str): The vehicle ID (from the first reading,
          or ``"unknown"`` if readings is empty).
        - ``features`` (dict[str, float]): Named feature values.
        - ``feature_names`` (list[str]): Ordered list of feature names.
        - ``reference_time`` (str): ISO 8601 reference time used.
        - ``sensor_types_found`` (list[str]): Unique sensor types seen.
    """
    if not readings:
        logger.info("No readings provided for feature extraction")
        return {
            "vehicle_id": "unknown",
            "features": {},
            "feature_names": [],
            "reference_time": (
                reference_time or datetime.now(timezone.utc)
            ).isoformat(),
            "sensor_types_found": [],
        }

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    # Determine the vehicle_id from readings (take first non-empty)
    vehicle_id = str(readings[0].get("vehicle_id", "unknown"))

    # Group values by sensor_type with parsed timestamps
    sensor_data: dict[str, list[tuple[datetime, float]]] = {}
    for r in readings:
        st = r.get("sensor_type")
        val = r.get("value")
        ts = r.get("timestamp")
        if st is None or val is None or ts is None:
            continue
        try:
            parsed_ts = _parse_timestamp(ts)
            float_val = float(val)
        except (ValueError, TypeError):
            continue

        if st not in sensor_data:
            sensor_data[st] = []
        sensor_data[st].append((parsed_ts, float_val))

    # Sort sensor types for deterministic ordering
    sorted_sensors = sorted(sensor_data.keys())

    features: dict[str, float] = {}
    feature_names: list[str] = []

    for sensor_type in sorted_sensors:
        entries = sensor_data[sensor_type]
        for window in WINDOW_CONFIGS:
            window_name = window["name"]
            window_seconds = int(window["seconds"])
            cutoff = reference_time - timedelta(seconds=window_seconds)

            # Filter values within window
            window_values = [
                val for ts, val in entries if ts >= cutoff
            ]

            stat_keys = ["mean", "std", "max", "min", "count"]
            if len(window_values) >= MIN_READINGS_PER_WINDOW:
                stats = _compute_stats(window_values)
            else:
                stats = {k: 0.0 for k in stat_keys}

            for stat_name in stat_keys:
                fname = f"{sensor_type}_{window_name}_{stat_name}"
                features[fname] = round(stats[stat_name], 6)
                feature_names.append(fname)

    logger.info(
        "Extracted %d features for vehicle %s across %d sensor types "
        "(%d raw readings, ref_time=%s)",
        len(features),
        vehicle_id,
        len(sorted_sensors),
        len(readings),
        reference_time.isoformat(),
    )

    return {
        "vehicle_id": vehicle_id,
        "features": features,
        "feature_names": feature_names,
        "reference_time": reference_time.isoformat(),
        "sensor_types_found": sorted_sensors,
    }


# ---------------------------------------------------------------------------
# Feature matrix builder
# ---------------------------------------------------------------------------

def build_feature_matrix(
    vehicle_features: list[dict],
) -> dict:
    """Build a numpy feature matrix from multiple vehicle feature dicts.

    Aligns all vehicle feature dicts to a common set of feature names
    (the union of all feature names seen). Missing features for a given
    vehicle are filled with ``0.0``.

    Args:
        vehicle_features: List of dicts as returned by
            ``extract_rolling_features``, each containing ``vehicle_id``,
            ``features``, and ``feature_names``.

    Returns:
        Dict with keys:
        - ``matrix`` (np.ndarray): 2D array of shape
          ``(n_vehicles, n_features)``.
        - ``vehicle_ids`` (list[str]): Vehicle IDs in row order.
        - ``feature_names`` (list[str]): Feature names in column order.

    Raises:
        ValueError: If *vehicle_features* is empty.
    """
    if not vehicle_features:
        raise ValueError(
            "vehicle_features must be non-empty to build a feature matrix"
        )

    # Collect the union of all feature names (sorted for determinism)
    all_feature_names: set[str] = set()
    for vf in vehicle_features:
        all_feature_names.update(vf.get("feature_names", []))

    sorted_feature_names = sorted(all_feature_names)

    if not sorted_feature_names:
        logger.warning(
            "No features found across %d vehicle feature dicts",
            len(vehicle_features),
        )
        return {
            "matrix": np.empty((len(vehicle_features), 0), dtype=np.float64),
            "vehicle_ids": [
                str(vf.get("vehicle_id", "unknown"))
                for vf in vehicle_features
            ],
            "feature_names": [],
        }

    n_vehicles = len(vehicle_features)
    n_features = len(sorted_feature_names)
    matrix = np.zeros((n_vehicles, n_features), dtype=np.float64)
    vehicle_ids: list[str] = []

    # Build a name-to-column index for fast lookup
    col_index = {name: i for i, name in enumerate(sorted_feature_names)}

    for row_idx, vf in enumerate(vehicle_features):
        vid = str(vf.get("vehicle_id", "unknown"))
        vehicle_ids.append(vid)

        feat_dict = vf.get("features", {})
        for fname, fval in feat_dict.items():
            col = col_index.get(fname)
            if col is not None:
                matrix[row_idx, col] = float(fval)

    logger.info(
        "Built feature matrix: %d vehicles x %d features",
        n_vehicles,
        n_features,
    )

    return {
        "matrix": matrix,
        "vehicle_ids": vehicle_ids,
        "feature_names": sorted_feature_names,
    }
