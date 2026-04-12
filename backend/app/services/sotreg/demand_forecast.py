"""LSTM Demand Forecasting Service.

Implements demand forecasting with 7-day lookback (336 timesteps at
30-min intervals) and 24h-ahead output (48 timesteps). Uses
TensorFlow/Keras LSTM architecture with Morocco-specific features
including Ramadan seasonality.

Session 119 — CDC SOTREG v5.0 Module M8/ML.
"""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

import numpy as np

from app.services.sotreg.ramadan_calendar import is_ramadan

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOOKBACK_STEPS = 336       # 7 days × 24h × 2 (30-min intervals)
FORECAST_STEPS = 48        # 24h ahead at 30-min intervals
FEATURE_NAMES = [
    "historical_demand",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_holiday",
    "is_ramadan",
    "temperature",
    "precipitation",
]
NUM_FEATURES = len(FEATURE_NAMES)

# Keras availability flag
HAS_KERAS = False
try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_KERAS = True
except ImportError:
    logger.info("TensorFlow/Keras not available. Using numpy-based mock model.")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ForecastConfig:
    """Configuration for demand forecast model."""

    lookback: int = LOOKBACK_STEPS
    horizon: int = FORECAST_STEPS
    lstm_units_1: int = 64
    dropout_rate: float = 0.2
    lstm_units_2: int = 32
    epochs: int = 50
    batch_size: int = 32
    patience: int = 10  # early stopping patience
    validation_split: float = 0.2


@dataclass
class ForecastResult:
    """Result of a demand forecast."""

    ligne_id: str
    forecast: list[float]  # 48 values (24h at 30-min)
    timestamps: list[str]  # ISO timestamps for each step
    metrics: dict = field(default_factory=dict)
    model_version: int | None = None


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------


def normalize_features(data: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Min-max normalize features to [0, 1] range.

    Args:
        data: Array of shape (timesteps, num_features).

    Returns:
        Tuple of (normalized_data, min_values, max_values).
    """
    mins = data.min(axis=0)
    maxs = data.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0  # avoid division by zero
    normalized = (data - mins) / ranges
    return normalized, mins, maxs


def denormalize(values: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Reverse min-max normalization for a single feature.

    Args:
        values: Normalized values.
        min_val: Original minimum.
        max_val: Original maximum.

    Returns:
        Denormalized values.
    """
    return values * (max_val - min_val) + min_val


def create_sliding_windows(
    data: np.ndarray,
    lookback: int = LOOKBACK_STEPS,
    horizon: int = FORECAST_STEPS,
    stride: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Create sliding window sequences for LSTM training.

    Args:
        data: Normalized array of shape (timesteps, num_features).
        lookback: Number of input timesteps.
        horizon: Number of output timesteps.
        stride: Window stride.

    Returns:
        Tuple of (X, y) where:
        - X has shape (n_windows, lookback, num_features)
        - y has shape (n_windows, horizon)
    """
    n = len(data)
    X_list: list[np.ndarray] = []
    y_list: list[np.ndarray] = []

    for i in range(0, n - lookback - horizon + 1, stride):
        X_list.append(data[i : i + lookback])
        # Target: demand column (index 0) for the next `horizon` steps
        y_list.append(data[i + lookback : i + lookback + horizon, 0])

    if not X_list:
        return np.empty((0, lookback, data.shape[1])), np.empty((0, horizon))

    return np.array(X_list), np.array(y_list)


def engineer_features(
    demand_values: list[float],
    start_date: date,
    temperatures: list[float] | None = None,
    precipitation: list[float] | None = None,
    holidays: set[date] | None = None,
) -> np.ndarray:
    """Build feature matrix from raw demand data.

    Generates features at 30-min intervals:
    - historical_demand
    - hour_of_day (0-23, normalized)
    - day_of_week (0-6, normalized)
    - is_weekend (0/1)
    - is_holiday (0/1)
    - is_ramadan (0/1)
    - temperature (°C)
    - precipitation (mm)

    Args:
        demand_values: List of demand values at 30-min intervals.
        start_date: Starting date.
        temperatures: Optional temperature values (same length).
        precipitation: Optional precipitation values (same length).
        holidays: Optional set of holiday dates.

    Returns:
        Array of shape (len(demand_values), NUM_FEATURES).
    """
    n = len(demand_values)
    features = np.zeros((n, NUM_FEATURES))

    holidays = holidays or set()

    for i in range(n):
        minutes_offset = i * 30
        dt = datetime(
            start_date.year, start_date.month, start_date.day,
            tzinfo=timezone.utc,
        ) + timedelta(minutes=minutes_offset)

        features[i, 0] = demand_values[i]
        features[i, 1] = dt.hour / 23.0
        features[i, 2] = dt.weekday() / 6.0
        features[i, 3] = 1.0 if dt.weekday() >= 5 else 0.0
        features[i, 4] = 1.0 if dt.date() in holidays else 0.0
        features[i, 5] = 1.0 if is_ramadan(dt.date()) else 0.0
        features[i, 6] = (temperatures[i] if temperatures and i < len(temperatures) else 20.0) / 50.0
        features[i, 7] = (precipitation[i] if precipitation and i < len(precipitation) else 0.0) / 100.0

    return features


# ---------------------------------------------------------------------------
# Model building
# ---------------------------------------------------------------------------


def build_lstm_model(
    config: ForecastConfig | None = None,
) -> Any:
    """Build the LSTM demand forecasting model.

    Architecture: LSTM(64) -> Dropout(0.2) -> LSTM(32) -> Dense(48)

    Args:
        config: Forecast configuration.

    Returns:
        Compiled Keras model (or dict mock if Keras unavailable).
    """
    if config is None:
        config = ForecastConfig()

    if HAS_KERAS:
        model = keras.Sequential([
            keras.layers.LSTM(
                config.lstm_units_1,
                return_sequences=True,
                input_shape=(config.lookback, NUM_FEATURES),
            ),
            keras.layers.Dropout(config.dropout_rate),
            keras.layers.LSTM(config.lstm_units_2),
            keras.layers.Dense(config.horizon),
        ])
        model.compile(optimizer="adam", loss="mae", metrics=["mse"])
        return model

    # Mock model for environments without TensorFlow
    logger.warning("Building mock LSTM model (no TensorFlow)")
    return {
        "type": "lstm_mock",
        "architecture": [
            f"LSTM({config.lstm_units_1})",
            f"Dropout({config.dropout_rate})",
            f"LSTM({config.lstm_units_2})",
            f"Dense({config.horizon})",
        ],
        "input_shape": (config.lookback, NUM_FEATURES),
        "output_shape": (config.horizon,),
        "compiled": True,
        "optimizer": "adam",
        "loss": "mae",
    }


# ---------------------------------------------------------------------------
# Training pipeline
# ---------------------------------------------------------------------------


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    config: ForecastConfig | None = None,
) -> tuple[Any, dict]:
    """Train the LSTM model with early stopping.

    Args:
        X_train: Training input (n, lookback, features).
        y_train: Training target (n, horizon).
        X_val: Validation input.
        y_val: Validation target.
        config: Forecast configuration.

    Returns:
        Tuple of (trained model, metrics dict).
    """
    if config is None:
        config = ForecastConfig()

    model = build_lstm_model(config)

    if HAS_KERAS:
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=config.patience,
                restore_best_weights=True,
            ),
        ]
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=config.epochs,
            batch_size=config.batch_size,
            callbacks=callbacks,
            verbose=0,
        )
        # Evaluate
        val_metrics = model.evaluate(X_val, y_val, verbose=0)
        mae = float(val_metrics[0])
        mse = float(val_metrics[1])
        rmse = float(np.sqrt(mse))

        return model, {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "epochs_trained": len(history.history["loss"]),
            "early_stopped": len(history.history["loss"]) < config.epochs,
        }

    # Mock training
    logger.info("Mock training LSTM model")
    mae = float(np.mean(np.abs(y_val - np.mean(y_train))))
    rmse = float(np.sqrt(np.mean((y_val - np.mean(y_train)) ** 2)))

    return model, {
        "mae": round(mae, 4),
        "mse": round(mae ** 2, 4),
        "rmse": round(rmse, 4),
        "epochs_trained": config.epochs,
        "early_stopped": False,
        "mock": True,
    }


def predict(
    model: Any,
    X: np.ndarray,
    min_demand: float = 0.0,
    max_demand: float = 1.0,
) -> np.ndarray:
    """Generate forecast predictions.

    Args:
        model: Trained Keras model or mock dict.
        X: Input array of shape (batch, lookback, features).
        min_demand: Min value for denormalization.
        max_demand: Max value for denormalization.

    Returns:
        Denormalized predictions of shape (batch, horizon).
    """
    if HAS_KERAS and hasattr(model, "predict"):
        raw = model.predict(X, verbose=0)
    else:
        # Mock prediction: return mean demand + small noise
        batch_size = X.shape[0]
        raw = np.full((batch_size, FORECAST_STEPS), 0.5) + np.random.randn(batch_size, FORECAST_STEPS) * 0.05

    # Denormalize and clamp to non-negative
    denormed = denormalize(raw, min_demand, max_demand)
    return np.maximum(denormed, 0.0)


# ---------------------------------------------------------------------------
# Full forecast pipeline
# ---------------------------------------------------------------------------


def generate_forecast(
    demand_history: list[float],
    start_date: date,
    config: ForecastConfig | None = None,
    temperatures: list[float] | None = None,
    precipitation: list[float] | None = None,
) -> ForecastResult:
    """Run the full demand forecast pipeline.

    Args:
        demand_history: Historical demand values (30-min intervals).
        start_date: Start date of the history.
        config: Forecast configuration.
        temperatures: Optional temperature data.
        precipitation: Optional precipitation data.

    Returns:
        ForecastResult with 48 forecast values.
    """
    if config is None:
        config = ForecastConfig()

    if len(demand_history) < config.lookback + config.horizon:
        # Not enough data — return zeros
        logger.warning(
            "Insufficient demand data (%d < %d required)",
            len(demand_history), config.lookback + config.horizon,
        )
        now = datetime.now(timezone.utc)
        return ForecastResult(
            ligne_id="",
            forecast=[0.0] * config.horizon,
            timestamps=[
                (now + timedelta(minutes=30 * i)).isoformat()
                for i in range(config.horizon)
            ],
            metrics={"error": "insufficient_data"},
        )

    # Feature engineering
    features = engineer_features(
        demand_history, start_date, temperatures, precipitation,
    )
    normalized, mins, maxs = normalize_features(features)

    # Create windows
    X, y = create_sliding_windows(normalized, config.lookback, config.horizon)

    if len(X) == 0:
        now = datetime.now(timezone.utc)
        return ForecastResult(
            ligne_id="",
            forecast=[0.0] * config.horizon,
            timestamps=[(now + timedelta(minutes=30 * i)).isoformat() for i in range(config.horizon)],
            metrics={"error": "no_windows"},
        )

    # Train/val split (chronological)
    split = int(len(X) * (1 - config.validation_split))
    X_train, y_train = X[:split], y[:split]
    X_val, y_val = X[split:], y[split:]

    if len(X_train) == 0 or len(X_val) == 0:
        X_train, y_train = X, y
        X_val, y_val = X[-1:], y[-1:]

    # Train
    model, metrics = train_model(X_train, y_train, X_val, y_val, config)

    # Predict next 24h using latest window
    last_window = normalized[-config.lookback:].reshape(1, config.lookback, NUM_FEATURES)
    forecast_raw = predict(model, last_window, mins[0], maxs[0])
    forecast_values = forecast_raw[0].tolist()

    # Generate timestamps
    last_dt = datetime(
        start_date.year, start_date.month, start_date.day,
        tzinfo=timezone.utc,
    ) + timedelta(minutes=30 * len(demand_history))
    timestamps = [
        (last_dt + timedelta(minutes=30 * i)).isoformat()
        for i in range(config.horizon)
    ]

    return ForecastResult(
        ligne_id="",
        forecast=forecast_values,
        timestamps=timestamps,
        metrics=metrics,
    )
