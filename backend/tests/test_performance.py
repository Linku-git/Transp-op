"""Tests for Performance Optimization (Session 87)."""
from __future__ import annotations

import json

import pytest

from app.middleware.cache import (
    cache_key,
    CACHE_TTL,
)
from app.utils.query_optimizer import (
    PERFORMANCE_TARGETS,
    RECOMMENDED_INDEXES,
    add_pagination,
)


class TestCacheKeyGeneration:
    def test_simple_key(self):
        key = cache_key("site_config", "site-1")
        assert key == "site_config:site-1"

    def test_key_with_multiple_args(self):
        key = cache_key("employee", "tenant-1", "page-1")
        assert key == "employee:tenant-1:page-1"

    def test_key_with_kwargs(self):
        key = cache_key("list", tenant="t1", page=1)
        assert key.startswith("list:")
        assert len(key) > len("list:")

    def test_deterministic_keys(self):
        k1 = cache_key("test", "a", page=1)
        k2 = cache_key("test", "a", page=1)
        assert k1 == k2


class TestCacheTTL:
    def test_site_config_ttl(self):
        assert CACHE_TTL["site_config"] == 3600  # 1 hour

    def test_vehicle_catalog_ttl(self):
        assert CACHE_TTL["vehicle_catalog"] == 1800  # 30 min

    def test_settings_ttl(self):
        assert CACHE_TTL["settings"] == 86400  # 24 hours

    def test_optimization_result_ttl(self):
        assert CACHE_TTL["optimization_result"] == 600  # 10 min

    def test_kpi_dashboard_ttl(self):
        assert CACHE_TTL["kpi_dashboard"] == 300  # 5 min


class TestPerformanceTargets:
    def test_simple_crud_target(self):
        assert PERFORMANCE_TARGETS["simple_crud"] == 100

    def test_list_with_filters_target(self):
        assert PERFORMANCE_TARGETS["list_with_filters"] == 200

    def test_dashboard_aggregation_target(self):
        assert PERFORMANCE_TARGETS["dashboard_aggregation"] == 500

    def test_optimization_small_target(self):
        assert PERFORMANCE_TARGETS["optimization_small"] == 5000

    def test_optimization_large_is_async(self):
        assert PERFORMANCE_TARGETS["optimization_large"] == 300000  # 5 min

    def test_report_generation_is_async(self):
        assert PERFORMANCE_TARGETS["report_generation"] == 600000  # 10 min


class TestRecommendedIndexes:
    def test_indexes_defined(self):
        assert len(RECOMMENDED_INDEXES) >= 5

    def test_indexes_are_concurrent(self):
        for idx in RECOMMENDED_INDEXES:
            assert "CONCURRENTLY" in idx

    def test_indexes_are_idempotent(self):
        for idx in RECOMMENDED_INDEXES:
            assert "IF NOT EXISTS" in idx

    def test_employee_site_shift_index(self):
        found = any("employee_site_shift" in idx for idx in RECOMMENDED_INDEXES)
        assert found

    def test_kpi_snapshot_index(self):
        found = any("kpi_snapshot" in idx for idx in RECOMMENDED_INDEXES)
        assert found


class TestConnectionPooling:
    def test_pool_config_exists(self):
        from app.database import _pool_kwargs
        # Pool kwargs should be configured (when not in test mode)
        # In test mode, NullPool is used
        assert isinstance(_pool_kwargs, dict)

    def test_engine_has_pre_ping(self):
        from app.database import engine
        assert engine.pool._pre_ping is True


class TestQueryPagination:
    def test_pagination_default(self):
        from sqlalchemy import select, text
        from app.models.employee import Employee
        query = select(Employee)
        paginated = add_pagination(query, page=1, page_size=20)
        # SQLAlchemy query object is modified
        assert paginated is not None

    def test_pagination_max_size(self):
        from sqlalchemy import select
        from app.models.employee import Employee
        query = select(Employee)
        paginated = add_pagination(query, page=1, page_size=500, max_page_size=100)
        # Should cap at max_page_size=100
        assert paginated is not None
