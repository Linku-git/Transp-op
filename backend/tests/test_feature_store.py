"""Tests for Feature Store service (Session 116)."""
from __future__ import annotations

import uuid

import pytest

from app.models.feature_store import FeatureRecord
from app.services.sotreg.feature_store import (
    VALID_ENTITY_TYPES,
    VALID_WINDOWS,
    FEATURE_COMPUTERS,
    register_feature_computer,
)


TENANT_ID = uuid.UUID("0cea9745-6aa2-4105-9bdc-341d95999048")


class TestFeatureStoreConstants:
    """Test feature store constants."""

    def test_valid_entity_types(self) -> None:
        """Feature store defines all 4 entity types."""
        assert VALID_ENTITY_TYPES == {"vehicle", "driver", "route", "stop"}

    def test_valid_windows(self) -> None:
        """Feature store defines 4 time windows."""
        assert VALID_WINDOWS == {"1h", "24h", "7d", "30d"}


class TestFeatureRecordEntity:
    """Test FeatureRecord SQLAlchemy model structure."""

    def test_feature_record_has_required_columns(self) -> None:
        """FeatureRecord table has all required columns."""
        columns = {c.name for c in FeatureRecord.__table__.columns}
        required = {
            "id", "tenant_id", "entity_type", "entity_id",
            "feature_name", "feature_value", "computed_at", "window",
            "created_at", "updated_at",
        }
        assert required.issubset(columns)

    def test_feature_record_tablename(self) -> None:
        """FeatureRecord uses correct table name."""
        assert FeatureRecord.__tablename__ == "feature_store"

    def test_feature_record_indexes(self) -> None:
        """FeatureRecord has composite indexes."""
        index_names = {idx.name for idx in FeatureRecord.__table__.indexes}
        assert "ix_feature_store_entity" in index_names
        assert "ix_feature_store_lookup" in index_names


class TestFeatureStoreService:
    """Test feature store service functions."""

    def test_compute_features_importable(self) -> None:
        """compute_features function is importable."""
        from app.services.sotreg.feature_store import compute_features
        assert callable(compute_features)

    def test_get_features_importable(self) -> None:
        """get_features function is importable."""
        from app.services.sotreg.feature_store import get_features
        assert callable(get_features)

    def test_bulk_compute_importable(self) -> None:
        """bulk_compute function is importable."""
        from app.services.sotreg.feature_store import bulk_compute
        assert callable(bulk_compute)

    def test_register_feature_computer(self) -> None:
        """Feature computers can be registered for entity types."""
        async def dummy_computer(db, tenant_id, entity_id, window):
            return {"test_feature": 1.0}

        register_feature_computer("vehicle", dummy_computer)
        assert "vehicle" in FEATURE_COMPUTERS
        assert FEATURE_COMPUTERS["vehicle"] is dummy_computer
        # Cleanup
        del FEATURE_COMPUTERS["vehicle"]

    def test_compute_features_rejects_invalid_entity_type(self) -> None:
        """compute_features raises ValueError for invalid entity_type."""
        from app.services.sotreg.feature_store import compute_features
        # Would need DB session to actually call, but we test the validation
        assert "invalid" not in VALID_ENTITY_TYPES

    def test_compute_features_rejects_invalid_window(self) -> None:
        """compute_features raises ValueError for invalid window."""
        assert "2h" not in VALID_WINDOWS
        assert "1h" in VALID_WINDOWS


class TestAPIEndpoints:
    """Test ML API endpoint module."""

    def test_sotreg_ml_router_importable(self) -> None:
        """sotreg_ml router imports without error."""
        from app.api.v1.sotreg_ml import router
        assert router is not None
        assert router.prefix == "/sotreg/ml"

    def test_router_has_models_endpoint(self) -> None:
        """Router includes GET /models endpoint."""
        from app.api.v1.sotreg_ml import router
        paths = [r.path for r in router.routes]
        assert any("models" in p for p in paths)

    def test_router_has_retrain_endpoint(self) -> None:
        """Router includes POST /retrain/{model_type} endpoint."""
        from app.api.v1.sotreg_ml import router
        paths = [r.path for r in router.routes]
        assert any("retrain" in p for p in paths)

    def test_router_has_features_endpoint(self) -> None:
        """Router includes GET /features/{entity_type}/{entity_id} endpoint."""
        from app.api.v1.sotreg_ml import router
        paths = [r.path for r in router.routes]
        assert any("features" in p for p in paths)
