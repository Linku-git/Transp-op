"""Query optimization utilities — prevent N+1 queries and optimize loading."""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Select
from sqlalchemy.orm import selectinload, joinedload

logger = logging.getLogger(__name__)


def optimize_employee_query(query: Select) -> Select:
    """Add eager loading for Employee relationships to prevent N+1."""
    from app.models.employee import Employee
    return query.options(
        selectinload(Employee.site),
    )


def optimize_site_query(query: Select) -> Select:
    """Add eager loading for Site relationships."""
    return query


def add_pagination(
    query: Select,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> Select:
    """Apply consistent pagination to a query."""
    effective_size = min(page_size, max_page_size)
    offset = (page - 1) * effective_size
    return query.offset(offset).limit(effective_size)


# Performance targets from PRD
PERFORMANCE_TARGETS = {
    "simple_crud": 100,        # ms
    "list_with_filters": 200,  # ms
    "dashboard_aggregation": 500, # ms
    "optimization_small": 5000, # ms (5s)
    "optimization_large": 300000, # ms (5min, async)
    "report_generation": 600000,  # ms (10min, async)
}

# Index recommendations based on query patterns
RECOMMENDED_INDEXES = [
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_employee_site_shift ON employee(site_id, shift_time)",
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_employee_department ON employee(department)",
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_employee_active ON employee(tenant_id) WHERE active = true",
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_content_delivery_completed ON content_delivery(completed_at) WHERE completed_at IS NOT NULL",
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_optimization_tenant_date ON optimization(tenant_id, created_at DESC)",
    "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_kpi_snapshot_type_date ON kpi_snapshot(kpi_type, recorded_at DESC)",
]
