from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sensor configuration
# ---------------------------------------------------------------------------

VALID_SENSOR_TYPES = [
    "vibration",
    "temperature",
    "pressure",
    "can_bus",
    "battery_voltage",
    "engine_rpm",
    "speed",
]

SENSOR_VALUE_RANGES: dict[str, tuple[float, float]] = {
    "vibration": (0.0, 100.0),        # g-force
    "temperature": (-40.0, 200.0),     # celsius
    "pressure": (0.0, 10.0),           # bar
    "can_bus": (0.0, 65535.0),         # raw CAN value
    "battery_voltage": (0.0, 800.0),   # volts
    "engine_rpm": (0.0, 10000.0),      # RPM
    "speed": (0.0, 200.0),            # km/h
}

SENSOR_UNITS: dict[str, str] = {
    "vibration": "g",
    "temperature": "C",
    "pressure": "bar",
    "can_bus": "raw",
    "battery_voltage": "V",
    "engine_rpm": "rpm",
    "speed": "km/h",
}

# Required keys in each reading dict
_REQUIRED_READING_KEYS = {"vehicle_id", "timestamp", "sensor_type", "value"}


# ---------------------------------------------------------------------------
# Single reading validation
# ---------------------------------------------------------------------------

def validate_reading(sensor_type: str, value: float) -> dict:
    """Validate a single telemetry reading against known sensor ranges.

    Args:
        sensor_type: The sensor type identifier (e.g. ``"vibration"``).
        value: The numeric reading value.

    Returns:
        Dict with keys:
        - ``valid`` (bool): Whether the reading is within accepted range.
        - ``error`` (str | None): Human-readable error if invalid, else None.
    """
    if sensor_type not in VALID_SENSOR_TYPES:
        return {
            "valid": False,
            "error": (
                f"Unknown sensor_type '{sensor_type}'. "
                f"Valid types: {VALID_SENSOR_TYPES}"
            ),
        }

    vmin, vmax = SENSOR_VALUE_RANGES[sensor_type]

    if not isinstance(value, (int, float)):
        return {
            "valid": False,
            "error": f"Value must be numeric, got {type(value).__name__}",
        }

    if value < vmin or value > vmax:
        return {
            "valid": False,
            "error": (
                f"Value {value} out of range for '{sensor_type}' "
                f"[{vmin}, {vmax}]"
            ),
        }

    return {"valid": True, "error": None}


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def _validate_reading_dict(reading: dict, index: int) -> str | None:
    """Validate the structure of a single reading dict.

    Returns an error message string if invalid, or None if valid.
    """
    missing = _REQUIRED_READING_KEYS - set(reading.keys())
    if missing:
        return f"Reading[{index}]: missing required keys {sorted(missing)}"

    if not reading.get("vehicle_id"):
        return f"Reading[{index}]: vehicle_id must be non-empty"

    # Validate timestamp
    ts = reading.get("timestamp")
    if ts is None:
        return f"Reading[{index}]: timestamp is required"

    if isinstance(ts, str):
        try:
            datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return (
                f"Reading[{index}]: invalid timestamp format '{ts}', "
                f"expected ISO 8601"
            )
    elif not isinstance(ts, datetime):
        return (
            f"Reading[{index}]: timestamp must be ISO 8601 string or "
            f"datetime, got {type(ts).__name__}"
        )

    # Validate value is numeric
    val = reading.get("value")
    if not isinstance(val, (int, float)):
        return (
            f"Reading[{index}]: value must be numeric, "
            f"got {type(val).__name__}"
        )

    return None


def process_telemetry_batch(readings: list[dict]) -> dict:
    """Process a batch of telemetry readings with validation.

    Each reading dict should contain:
    - ``vehicle_id`` (str): Vehicle identifier.
    - ``timestamp`` (str | datetime): ISO 8601 timestamp.
    - ``sensor_type`` (str): Sensor type identifier.
    - ``value`` (float): Sensor reading value.
    - ``unit`` (str, optional): Measurement unit.
    - ``metadata`` (dict, optional): Additional metadata.

    Readings that fail structural or range validation are rejected.
    Valid readings are returned with normalized timestamps and units.

    Args:
        readings: List of reading dicts.

    Returns:
        Dict with keys:
        - ``accepted`` (int): Number of accepted readings.
        - ``rejected`` (int): Number of rejected readings.
        - ``errors`` (list[dict]): List of error details for rejected
          readings, each with ``index``, ``vehicle_id``, and ``error``.
        - ``accepted_readings`` (list[dict]): Validated and normalized
          readings ready for storage.
    """
    if not readings:
        logger.info("Empty telemetry batch received, nothing to process")
        return {
            "accepted": 0,
            "rejected": 0,
            "errors": [],
            "accepted_readings": [],
        }

    accepted_readings: list[dict] = []
    errors: list[dict] = []

    for idx, reading in enumerate(readings):
        vehicle_id = reading.get("vehicle_id", "<unknown>")

        # Structural validation
        struct_error = _validate_reading_dict(reading, idx)
        if struct_error is not None:
            errors.append({
                "index": idx,
                "vehicle_id": str(vehicle_id),
                "error": struct_error,
            })
            continue

        # Sensor type and value range validation
        sensor_type = reading["sensor_type"]
        value = float(reading["value"])
        validation = validate_reading(sensor_type, value)

        if not validation["valid"]:
            errors.append({
                "index": idx,
                "vehicle_id": str(vehicle_id),
                "error": validation["error"],
            })
            continue

        # Normalize timestamp to datetime
        ts = reading["timestamp"]
        if isinstance(ts, str):
            normalized_ts = datetime.fromisoformat(
                ts.replace("Z", "+00:00")
            )
        else:
            normalized_ts = ts

        # Build normalized reading
        accepted_readings.append({
            "vehicle_id": str(reading["vehicle_id"]),
            "timestamp": normalized_ts,
            "sensor_type": sensor_type,
            "value": value,
            "unit": reading.get("unit") or SENSOR_UNITS.get(sensor_type, ""),
            "metadata": reading.get("metadata") or {},
        })

    accepted = len(accepted_readings)
    rejected = len(errors)

    logger.info(
        "Telemetry batch processed: %d accepted, %d rejected out of %d total",
        accepted,
        rejected,
        len(readings),
    )

    if errors:
        logger.warning(
            "Telemetry batch had %d validation errors (first: %s)",
            rejected,
            errors[0]["error"],
        )

    return {
        "accepted": accepted,
        "rejected": rejected,
        "errors": errors,
        "accepted_readings": accepted_readings,
    }
