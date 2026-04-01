from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.optimization_pipeline import (
    PipelineParams,
    PipelineMetrics,
    PipelineResult,
    calculate_metrics,
    run_optimization_pipeline,
)
from app.services.clustering import ClusterResult, EmployeePoint
from app.services.vehicle_assignment import (
    AssignmentResult,
    AssignmentSummary,
    VehicleCandidate,
)
from app.services.routing import RoutingResult, OptimizedRoute, RouteStop
from app.schemas.optimization import (
    OptimizationHistoryItem,
    OptimizationFullResponse,
    ClusterResponse,
)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_employee(
    lat: float = 33.5, lng: float = -7.6, is_pmr: bool = False
) -> EmployeePoint:
    eid = uuid.uuid4()
    return EmployeePoint(employee_id=eid, lat=lat, lng=lng, is_pmr=is_pmr)


def _make_vehicle(
    capacity: int = 10, pmr: bool = False, zfe: bool = False
) -> VehicleCandidate:
    return VehicleCandidate(
        vehicle_id=uuid.uuid4(),
        capacity=capacity,
        is_pmr_accessible=pmr,
        zfe_compliant=zfe,
        type="Minibus",
    )


def _build_pipeline_inputs(
    employees: list[EmployeePoint],
    vehicles: list[VehicleCandidate],
    site_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
) -> dict:
    """Build the keyword arguments required by run_optimization_pipeline."""
    s_id = site_id or uuid.uuid4()
    t_id = tenant_id or uuid.uuid4()

    employee_locations = {
        emp.employee_id: (emp.lat, emp.lng) for emp in employees
    }
    employee_pmr = {emp.employee_id: emp.is_pmr for emp in employees}

    params = PipelineParams(
        site_id=s_id,
        tenant_id=t_id,
        use_osrm=False,
        algorithm="dbscan",
        eps_meters=2000.0,
        min_samples=2,
    )

    return {
        "params": params,
        "employees": employees,
        "employee_leave_ids": set(),
        "vehicles": vehicles,
        "volunteer_drivers": [],
        "site_lat": 33.5731,
        "site_lng": -7.5898,
        "site_zfe": False,
        "employee_locations": employee_locations,
        "employee_pmr": employee_pmr,
    }


# ---------------------------------------------------------------------------
# 1. test_full_pipeline (async)
# ---------------------------------------------------------------------------


async def test_full_pipeline() -> None:
    """Full pipeline with 5 employees and 2 vehicles produces a completed result."""
    employees = [
        _make_employee(lat=33.55, lng=-7.60),
        _make_employee(lat=33.56, lng=-7.61),
        _make_employee(lat=33.54, lng=-7.59),
        _make_employee(lat=33.57, lng=-7.62),
        _make_employee(lat=33.53, lng=-7.58),
    ]
    vehicles = [
        _make_vehicle(capacity=3),
        _make_vehicle(capacity=3),
    ]

    kwargs = _build_pipeline_inputs(employees, vehicles)
    result = await run_optimization_pipeline(**kwargs)

    assert result.status == "completed"
    assert result.clusters is not None
    assert len(result.clusters) > 0
    assert result.assignments is not None
    assert len(result.assignments) > 0
    assert result.metrics is not None
    assert result.metrics.total_employees == 5


# ---------------------------------------------------------------------------
# 2. test_leave_exclusion (async)
# ---------------------------------------------------------------------------


async def test_leave_exclusion() -> None:
    """Employees on leave are excluded from the pipeline metrics."""
    employees = [
        _make_employee(lat=33.55, lng=-7.60),
        _make_employee(lat=33.56, lng=-7.61),
        _make_employee(lat=33.54, lng=-7.59),
        _make_employee(lat=33.57, lng=-7.62),
        _make_employee(lat=33.53, lng=-7.58),
    ]
    leave_ids = {employees[0].employee_id, employees[1].employee_id}

    vehicles = [
        _make_vehicle(capacity=5),
    ]

    kwargs = _build_pipeline_inputs(employees, vehicles)
    kwargs["employee_leave_ids"] = leave_ids

    result = await run_optimization_pipeline(**kwargs)

    assert result.status == "completed"
    assert result.metrics is not None
    assert result.metrics.employees_excluded_leave == 2
    assert result.metrics.total_employees == 5


# ---------------------------------------------------------------------------
# 3. test_metrics_calculation (sync)
# ---------------------------------------------------------------------------


def test_metrics_calculation() -> None:
    """calculate_metrics produces correct fuel, cost, CO2, and time-saved values."""
    clusters = [
        ClusterResult(
            centroid_lat=33.5 + i * 0.01,
            centroid_lng=-7.6 + i * 0.01,
            employee_ids=[uuid.uuid4() for _ in range(5)],
            pmr_count=0,
            employee_count=5,
        )
        for i in range(4)
    ]

    assignment_summary = AssignmentSummary(
        assignments=[],
        total_vehicles_used=4,
        total_employees_assigned=17,
        avg_occupancy_rate=0.85,
        unassigned_clusters=[],
    )

    routing_result = RoutingResult(
        routes=[],
        total_distance_km=100.0,
        total_duration_minutes=120.0,
    )

    metrics = calculate_metrics(
        total_employees=20,
        employees_excluded=3,
        clusters=clusters,
        assignment_summary=assignment_summary,
        routing_result=routing_result,
    )

    assert metrics.total_employees == 20
    assert metrics.employees_assigned == 17
    assert metrics.employees_excluded_leave == 3
    assert metrics.total_clusters == 4
    assert metrics.total_vehicles_used == 4

    # Fuel: 100 km * 15 L/100km = 15.0 L
    assert metrics.estimated_fuel_liters == 15.0

    # Cost: 15.0 * 12 MAD/L = 180.0 MAD
    assert metrics.estimated_fuel_cost_mad == 180.0

    # CO2: 15.0 * 2.68 kg/L = 40.2 kg
    assert metrics.co2_estimate_kg == 40.2

    # Time saved: (17 * 45 * 2 - 120) / 60 = (1530 - 120) / 60 = 23.5 h
    assert metrics.time_saved_vs_individual_hours > 0
    assert metrics.time_saved_vs_individual_hours == 23.5


# ---------------------------------------------------------------------------
# 4. test_celery_task (sync -- progress tracking via mocked Redis)
# ---------------------------------------------------------------------------


def test_celery_task_progress_tracking() -> None:
    """set_optimization_status / get_optimization_status round-trip via mocked Redis."""
    from app.tasks.optimization_tasks import (
        set_optimization_status,
        get_optimization_status,
    )

    opt_id = uuid.uuid4()
    mock_redis = MagicMock()
    stored: dict[str, str] = {}

    def mock_set(key: str, value: str, ex: int = 0) -> None:
        stored[key] = value

    def mock_get(key: str) -> str | None:
        return stored.get(key)

    mock_redis.set = mock_set
    mock_redis.get = mock_get

    with patch("app.tasks.optimization_tasks._get_redis", return_value=mock_redis):
        set_optimization_status(opt_id, "running", 0.5, "Processing")
        result = get_optimization_status(opt_id)

    assert result is not None
    assert result["status"] == "running"
    assert result["progress"] == 0.5
    assert result["step"] == "Processing"


# ---------------------------------------------------------------------------
# 5. test_optimization_status (sync -- multiple status values)
# ---------------------------------------------------------------------------


def test_optimization_status_values() -> None:
    """Different status values are stored and retrieved correctly."""
    from app.tasks.optimization_tasks import (
        set_optimization_status,
        get_optimization_status,
    )

    mock_redis = MagicMock()
    stored: dict[str, str] = {}

    def mock_set(key: str, value: str, ex: int = 0) -> None:
        stored[key] = value

    def mock_get(key: str) -> str | None:
        return stored.get(key)

    mock_redis.set = mock_set
    mock_redis.get = mock_get

    with patch("app.tasks.optimization_tasks._get_redis", return_value=mock_redis):
        # Pending
        opt_id_1 = uuid.uuid4()
        set_optimization_status(opt_id_1, "pending", 0.0, "Queued")
        r1 = get_optimization_status(opt_id_1)
        assert r1 is not None
        assert r1["status"] == "pending"
        assert r1["progress"] == 0.0
        assert r1["step"] == "Queued"

        # Completed
        opt_id_2 = uuid.uuid4()
        set_optimization_status(opt_id_2, "completed", 1.0, "Done")
        r2 = get_optimization_status(opt_id_2)
        assert r2 is not None
        assert r2["status"] == "completed"
        assert r2["progress"] == 1.0

        # Failed (with error)
        opt_id_3 = uuid.uuid4()
        set_optimization_status(
            opt_id_3, "failed", 0.0, "Error", error="Something broke"
        )
        r3 = get_optimization_status(opt_id_3)
        assert r3 is not None
        assert r3["status"] == "failed"
        assert r3["error"] == "Something broke"


# ---------------------------------------------------------------------------
# 6. test_optimization_history (sync -- schema serialization)
# ---------------------------------------------------------------------------


def test_optimization_history_schema() -> None:
    """OptimizationHistoryItem serialises correctly; site_name can be None."""
    now = datetime.now(timezone.utc)
    item = OptimizationHistoryItem(
        id=uuid.uuid4(),
        site_id=uuid.uuid4(),
        condition_type="normal",
        status="completed",
        metrics={"total_employees": 50, "total_clusters": 5},
        target_date=date(2026, 4, 1),
        created_at=now,
        completed_at=now,
        site_name=None,
    )

    dumped = item.model_dump()
    assert dumped["status"] == "completed"
    assert dumped["site_name"] is None
    assert dumped["metrics"]["total_employees"] == 50
    assert dumped["condition_type"] == "normal"

    # Also verify with a non-None site_name
    item_with_name = item.model_copy(update={"site_name": "Casablanca HQ"})
    dumped2 = item_with_name.model_dump()
    assert dumped2["site_name"] == "Casablanca HQ"


# ---------------------------------------------------------------------------
# 7. test_latest_result (sync -- OptimizationFullResponse schema)
# ---------------------------------------------------------------------------


def test_latest_result_schema() -> None:
    """OptimizationFullResponse serialises; clusters can be an empty list."""
    now = datetime.now(timezone.utc)
    resp = OptimizationFullResponse(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        site_id=None,
        condition_type="rain",
        status="completed",
        params={"algorithm": "dbscan", "eps_meters": 500.0},
        metrics={"total_employees": 30, "total_clusters": 3},
        target_date=None,
        created_at=now,
        completed_at=now,
        clusters=[],
        routes=[],
    )

    dumped = resp.model_dump()
    assert dumped["status"] == "completed"
    assert dumped["clusters"] == []
    assert dumped["site_id"] is None
    assert dumped["target_date"] is None
    assert dumped["params"]["algorithm"] == "dbscan"

    # Verify routes can hold arbitrary dicts
    resp_with_routes = resp.model_copy(
        update={"routes": [{"vehicle_id": str(uuid.uuid4()), "stops": []}]}
    )
    dumped2 = resp_with_routes.model_dump()
    assert len(dumped2["routes"]) == 1


# ---------------------------------------------------------------------------
# 8. test_multi_site_optimization (async)
# ---------------------------------------------------------------------------


async def test_multi_site_optimization() -> None:
    """Two independent site runs produce valid results with no cross-contamination."""
    # Casablanca employees (around 33.5, -7.6)
    casa_employees = [
        _make_employee(lat=33.55, lng=-7.60),
        _make_employee(lat=33.56, lng=-7.61),
        _make_employee(lat=33.54, lng=-7.59),
    ]
    casa_vehicles = [_make_vehicle(capacity=5)]

    # Rabat employees (around 34.0, -6.8) -- far from Casablanca
    rabat_employees = [
        _make_employee(lat=34.00, lng=-6.80),
        _make_employee(lat=34.01, lng=-6.81),
        _make_employee(lat=33.99, lng=-6.79),
    ]
    rabat_vehicles = [_make_vehicle(capacity=5)]

    casa_kwargs = _build_pipeline_inputs(casa_employees, casa_vehicles)
    casa_kwargs["site_lat"] = 33.5731
    casa_kwargs["site_lng"] = -7.5898

    rabat_kwargs = _build_pipeline_inputs(rabat_employees, rabat_vehicles)
    rabat_kwargs["site_lat"] = 34.0209
    rabat_kwargs["site_lng"] = -6.8416

    result_casa = await run_optimization_pipeline(**casa_kwargs)
    result_rabat = await run_optimization_pipeline(**rabat_kwargs)

    assert result_casa.status == "completed"
    assert result_rabat.status == "completed"

    assert result_casa.clusters is not None
    assert result_rabat.clusters is not None
    assert len(result_casa.clusters) > 0
    assert len(result_rabat.clusters) > 0

    # Collect all employee IDs across clusters for each result
    casa_cluster_emp_ids: set[uuid.UUID] = set()
    for cluster in result_casa.clusters:
        casa_cluster_emp_ids.update(cluster.employee_ids)

    rabat_cluster_emp_ids: set[uuid.UUID] = set()
    for cluster in result_rabat.clusters:
        rabat_cluster_emp_ids.update(cluster.employee_ids)

    # No cross-contamination: the two sets must be completely disjoint
    assert casa_cluster_emp_ids.isdisjoint(rabat_cluster_emp_ids)

    # Each result should contain only its own employees
    casa_input_ids = {e.employee_id for e in casa_employees}
    rabat_input_ids = {e.employee_id for e in rabat_employees}

    assert casa_cluster_emp_ids.issubset(casa_input_ids)
    assert rabat_cluster_emp_ids.issubset(rabat_input_ids)
