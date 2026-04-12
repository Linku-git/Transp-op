"""Tests for LSTM Demand Forecasting service (Session 119)."""
from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from app.services.sotreg.demand_forecast import (
    FORECAST_STEPS,
    LOOKBACK_STEPS,
    NUM_FEATURES,
    ForecastConfig,
    ForecastResult,
    build_lstm_model,
    create_sliding_windows,
    denormalize,
    engineer_features,
    generate_forecast,
    normalize_features,
    predict,
    train_model,
)


# ---------------------------------------------------------------------------
# Feature engineering tests
# ---------------------------------------------------------------------------


class TestFeatureEngineering:
    """Tests for feature engineering pipeline."""

    def test_engineer_features_shape(self) -> None:
        """Feature matrix has correct shape (n, num_features)."""
        demand = [10.0] * 100
        features = engineer_features(demand, date(2026, 3, 1))
        assert features.shape == (100, NUM_FEATURES)

    def test_normalization_range(self) -> None:
        """Normalized features are in [0, 1] range."""
        data = np.random.rand(50, 5) * 100
        normalized, mins, maxs = normalize_features(data)
        assert normalized.min() >= -0.001
        assert normalized.max() <= 1.001

    def test_denormalize_roundtrip(self) -> None:
        """Normalize then denormalize returns original values."""
        original = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        min_val, max_val = 10.0, 50.0
        normed = (original - min_val) / (max_val - min_val)
        restored = denormalize(normed, min_val, max_val)
        np.testing.assert_array_almost_equal(restored, original)

    def test_engineer_features_handles_missing_weather(self) -> None:
        """Feature engineering handles missing weather data gracefully."""
        demand = [10.0] * 50
        # No temperatures or precipitation provided
        features = engineer_features(demand, date(2026, 3, 1))
        assert features.shape == (50, NUM_FEATURES)
        # Temperature column should have default values
        assert np.all(features[:, 6] >= 0)


class TestSlidingWindows:
    """Tests for sliding window generation."""

    def test_correct_input_shape(self) -> None:
        """Sliding window X has shape (batch, lookback, features)."""
        data = np.random.rand(500, NUM_FEATURES)
        X, y = create_sliding_windows(data, lookback=100, horizon=48)
        assert X.shape[1] == 100
        assert X.shape[2] == NUM_FEATURES

    def test_correct_output_shape(self) -> None:
        """Sliding window y has shape (batch, horizon)."""
        data = np.random.rand(500, NUM_FEATURES)
        X, y = create_sliding_windows(data, lookback=100, horizon=48)
        assert y.shape[1] == 48

    def test_window_count(self) -> None:
        """Correct number of windows generated."""
        n = 500
        lookback = 100
        horizon = 48
        data = np.random.rand(n, NUM_FEATURES)
        X, y = create_sliding_windows(data, lookback, horizon, stride=1)
        expected = n - lookback - horizon + 1
        assert len(X) == expected

    def test_empty_data(self) -> None:
        """Empty data returns empty windows."""
        data = np.empty((0, NUM_FEATURES))
        X, y = create_sliding_windows(data, lookback=100, horizon=48)
        assert len(X) == 0
        assert len(y) == 0

    def test_insufficient_data(self) -> None:
        """Data shorter than lookback+horizon returns empty."""
        data = np.random.rand(50, NUM_FEATURES)  # < 100+48
        X, y = create_sliding_windows(data, lookback=100, horizon=48)
        assert len(X) == 0


class TestModel:
    """Tests for LSTM model building and training."""

    def test_build_model_compiles(self) -> None:
        """Model builds without error (Keras or mock)."""
        model = build_lstm_model()
        assert model is not None

    def test_model_architecture(self) -> None:
        """Model has correct architecture description."""
        model = build_lstm_model()
        if isinstance(model, dict):
            # Mock model
            assert "LSTM(64)" in model["architecture"]
            assert "Dropout(0.2)" in model["architecture"]
            assert "LSTM(32)" in model["architecture"]
            assert "Dense(48)" in model["architecture"]
        else:
            # Real Keras model
            assert len(model.layers) == 4

    def test_training_pipeline_runs(self) -> None:
        """Training pipeline completes with synthetic data."""
        config = ForecastConfig(
            lookback=20, horizon=10, epochs=2, batch_size=4,
            lstm_units_1=8, lstm_units_2=4,
        )
        n = 100
        X = np.random.rand(n, config.lookback, NUM_FEATURES)
        y = np.random.rand(n, config.horizon)
        split = int(n * 0.8)

        model, metrics = train_model(
            X[:split], y[:split], X[split:], y[split:], config,
        )
        assert model is not None
        assert "mae" in metrics
        assert "rmse" in metrics

    def test_predict_output_shape(self) -> None:
        """Predict returns correct output shape."""
        config = ForecastConfig(lookback=20, horizon=FORECAST_STEPS, lstm_units_1=8, lstm_units_2=4)
        model = build_lstm_model(config)
        X = np.random.rand(5, 20, NUM_FEATURES)
        preds = predict(model, X, min_demand=0, max_demand=100)
        assert preds.shape == (5, FORECAST_STEPS)

    def test_predictions_non_negative(self) -> None:
        """Forecast values are non-negative (demand >= 0)."""
        config = ForecastConfig(lookback=20, horizon=10, lstm_units_1=8, lstm_units_2=4)
        model = build_lstm_model(config)
        X = np.random.rand(3, 20, NUM_FEATURES)
        preds = predict(model, X, min_demand=0, max_demand=50)
        assert np.all(preds >= 0)


class TestForecastPipeline:
    """Tests for the full forecast pipeline."""

    def test_generate_forecast_output_length(self) -> None:
        """Forecast produces 48 values (24h at 30-min intervals)."""
        config = ForecastConfig(
            lookback=50, horizon=48, epochs=2, batch_size=4,
            lstm_units_1=8, lstm_units_2=4,
        )
        demand = list(np.random.rand(200) * 50)
        result = generate_forecast(demand, date(2026, 3, 1), config)
        assert len(result.forecast) == 48
        assert len(result.timestamps) == 48

    def test_generate_forecast_insufficient_data(self) -> None:
        """Insufficient data returns graceful error result."""
        config = ForecastConfig(lookback=100, horizon=48)
        demand = [10.0] * 50  # < 100 + 48
        result = generate_forecast(demand, date(2026, 3, 1), config)
        assert len(result.forecast) == 48
        assert result.metrics.get("error") == "insufficient_data"

    def test_forecast_result_dataclass(self) -> None:
        """ForecastResult has all expected fields."""
        result = ForecastResult(
            ligne_id="abc-123",
            forecast=[1.0] * 48,
            timestamps=["2026-03-01T00:00:00"] * 48,
            metrics={"mae": 3.2},
        )
        assert result.ligne_id == "abc-123"
        assert len(result.forecast) == 48


class TestSchemas:
    """Tests for forecast Pydantic schemas."""

    def test_forecast_request_schema(self) -> None:
        """DemandForecastRequest validates correctly."""
        from app.schemas.demand_forecast import DemandForecastRequest
        req = DemandForecastRequest(ligne_id="test-123")
        assert req.lookback_days == 7
        assert req.include_weather is True

    def test_forecast_response_schema(self) -> None:
        """DemandForecastResponse accepts 48-step forecast."""
        from app.schemas.demand_forecast import DemandForecastResponse
        resp = DemandForecastResponse(
            ligne_id="test-123",
            forecast=[1.0] * 48,
            timestamps=["2026-03-01T00:00:00"] * 48,
        )
        assert len(resp.forecast) == 48
        assert resp.horizon_hours == 24

    def test_api_endpoints_registered(self) -> None:
        """Forecast API endpoints are registered."""
        from app.api.v1.sotreg_ml import router
        paths = [r.path for r in router.routes]
        assert any("forecast" in p for p in paths)
