"""Tests for ML Model Registry service (Session 116)."""
from __future__ import annotations

import uuid

import pytest

from app.models.ml_model import MLModel
from app.services.sotreg.model_registry import (
    MODEL_STORAGE_DIR,
    VALID_MODEL_TYPES,
    VALID_STATUSES,
)


TENANT_ID = uuid.UUID("0cea9745-6aa2-4105-9bdc-341d95999048")


class TestMLModelConstants:
    """Test model registry constants and configuration."""

    def test_valid_model_types(self) -> None:
        """Registry defines all 3 model types."""
        assert VALID_MODEL_TYPES == {"isolation_forest", "random_forest", "lstm"}

    def test_valid_statuses(self) -> None:
        """Registry defines 4 lifecycle statuses."""
        assert VALID_STATUSES == {"training", "ready", "promoted", "retired"}

    def test_storage_dir_defined(self) -> None:
        """Model storage directory is configured."""
        assert MODEL_STORAGE_DIR is not None
        assert isinstance(MODEL_STORAGE_DIR, str)


class TestMLModelEntity:
    """Test MLModel SQLAlchemy model structure."""

    def test_ml_model_has_required_columns(self) -> None:
        """MLModel table has all required columns."""
        columns = {c.name for c in MLModel.__table__.columns}
        required = {
            "id", "tenant_id", "model_type", "version", "status",
            "metrics", "file_path", "trained_at", "feature_names",
            "created_at", "updated_at",
        }
        assert required.issubset(columns)

    def test_ml_model_tablename(self) -> None:
        """MLModel uses correct table name."""
        assert MLModel.__tablename__ == "ml_model"

    def test_ml_model_indexes(self) -> None:
        """MLModel has composite indexes."""
        index_names = {idx.name for idx in MLModel.__table__.indexes}
        assert "ix_ml_model_tenant_type" in index_names
        assert "ix_ml_model_tenant_status" in index_names


class TestModelRegistryService:
    """Test model registry service functions."""

    def test_save_model_importable(self) -> None:
        """save_model function is importable."""
        from app.services.sotreg.model_registry import save_model
        assert callable(save_model)

    def test_load_model_importable(self) -> None:
        """load_model function is importable."""
        from app.services.sotreg.model_registry import load_model
        assert callable(load_model)

    def test_promote_importable(self) -> None:
        """promote function is importable."""
        from app.services.sotreg.model_registry import promote
        assert callable(promote)

    def test_retire_importable(self) -> None:
        """retire function is importable."""
        from app.services.sotreg.model_registry import retire
        assert callable(retire)

    def test_list_models_importable(self) -> None:
        """list_models function is importable."""
        from app.services.sotreg.model_registry import list_models
        assert callable(list_models)


class TestModelSerialization:
    """Test model serialization patterns."""

    def test_joblib_available(self) -> None:
        """joblib is available for model serialization."""
        import joblib
        assert hasattr(joblib, "dump")
        assert hasattr(joblib, "load")

    def test_joblib_roundtrip(self, tmp_path: str) -> None:
        """joblib can serialize and deserialize sklearn model."""
        import joblib
        import os
        from sklearn.ensemble import IsolationForest

        model = IsolationForest(n_estimators=10, random_state=42)
        import numpy as np
        X = np.random.randn(50, 3)
        model.fit(X)

        path = os.path.join(tmp_path, "test_model.joblib")
        joblib.dump(model, path)
        loaded = joblib.load(path)

        assert hasattr(loaded, "predict")
        preds_orig = model.predict(X)
        preds_loaded = loaded.predict(X)
        np.testing.assert_array_equal(preds_orig, preds_loaded)

    def test_sklearn_isolation_forest_fits(self) -> None:
        """IsolationForest trains and produces predictions."""
        from sklearn.ensemble import IsolationForest
        import numpy as np

        model = IsolationForest(n_estimators=10, random_state=42)
        X = np.random.randn(100, 5)
        model.fit(X)
        preds = model.predict(X)
        assert len(preds) == 100
        assert set(preds).issubset({-1, 1})

    def test_sklearn_random_forest_fits(self) -> None:
        """RandomForestClassifier trains and produces predictions."""
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.randn(100, 8)
        y = (X[:, 0] > 0).astype(int)
        model.fit(X, y)
        preds = model.predict(X)
        assert len(preds) == 100


class TestRetrainTask:
    """Test ML retraining task."""

    def test_retrain_module_importable(self) -> None:
        """Retrain module imports without error."""
        from app.tasks.ml_retrain import run_retrain_task, run_retrain_sync
        assert callable(run_retrain_task)
        assert callable(run_retrain_sync)

    def test_beat_schedule_defined(self) -> None:
        """Retraining beat schedule includes all 3 model types."""
        from app.tasks.ml_retrain import ML_RETRAIN_BEAT_SCHEDULE
        assert len(ML_RETRAIN_BEAT_SCHEDULE) == 3
        keys = set(ML_RETRAIN_BEAT_SCHEDULE.keys())
        assert any("isolation" in k for k in keys)
        assert any("random" in k for k in keys)
        assert any("lstm" in k for k in keys)


class TestMLSchemas:
    """Test Pydantic schemas."""

    def test_ml_model_response_schema(self) -> None:
        """MLModelResponse can be constructed."""
        from app.schemas.ml_model import MLModelResponse
        from datetime import datetime, timezone

        data = MLModelResponse(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            model_type="isolation_forest",
            version=1,
            status="ready",
            metrics={"accuracy": 0.92},
            file_path="/tmp/test.joblib",
            trained_at=datetime.now(timezone.utc),
            feature_names=["f1", "f2"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert data.model_type == "isolation_forest"
        assert data.version == 1

    def test_retrain_request_defaults(self) -> None:
        """RetrainRequest has default force=False."""
        from app.schemas.ml_model import RetrainRequest
        req = RetrainRequest()
        assert req.force is False

    def test_feature_response_schema(self) -> None:
        """FeatureResponse can be constructed."""
        from app.schemas.ml_model import FeatureResponse
        data = FeatureResponse(
            entity_type="vehicle",
            entity_id=uuid.uuid4(),
            features={"speed": 45.0, "fuel": 8.5},
            window="24h",
        )
        assert data.entity_type == "vehicle"
        assert len(data.features) == 2
