from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import date as date_type, datetime, timezone

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis-based progress tracking
# ---------------------------------------------------------------------------

_redis: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    """Lazily initialise and return a Redis client."""
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def set_optimization_status(
    optimization_id: uuid.UUID,
    status: str,
    progress: float = 0.0,
    step: str = "",
    error: str | None = None,
) -> None:
    """Store optimization progress in Redis (1 h TTL)."""
    r = _get_redis()
    key = f"optimization:{optimization_id}:status"
    data = {
        "status": status,
        "progress": progress,
        "step": step,
        "error": error or "",
    }
    r.set(key, json.dumps(data), ex=3600)


def get_optimization_status(optimization_id: uuid.UUID) -> dict | None:
    """Retrieve optimization progress from Redis."""
    r = _get_redis()
    key = f"optimization:{optimization_id}:status"
    raw = r.get(key)
    if raw is None:
        return None
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Celery setup (graceful degradation)
# ---------------------------------------------------------------------------

try:
    from celery import Celery

    celery_app = Celery(
        "transpop",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.task_track_started = True
    celery_app.conf.task_time_limit = 300  # 5 min hard limit
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    celery_app = None
    logger.warning("Celery not available. Optimization tasks will run synchronously.")


# ---------------------------------------------------------------------------
# Main pipeline task
# ---------------------------------------------------------------------------


async def run_optimization_task(
    optimization_id: str,
    site_id: str,
    tenant_id: str,
    condition_type: str = "normal",
    target_date: str | None = None,
    algorithm: str = "dbscan",
    eps_meters: float = 500.0,
    min_samples: int = 2,
    n_clusters: int | None = None,
    max_cluster_size: int | None = None,
    max_walking_distance_meters: float = 800.0,
    max_route_duration_seconds: int = 5400,
    include_volunteers: bool = False,
    use_osrm: bool = True,
) -> dict:
    """Run the full optimization pipeline.

    This is the main entry point.  It loads data from the database,
    runs clustering + vehicle assignment + route optimisation, saves
    results to the database, and returns a summary dict.

    The function can be called directly (``await run_optimization_task(...)``)
    or wrapped in a Celery task once the broker is fully configured.

    Args:
        optimization_id: UUID of the pre-created Optimization record.
        site_id: UUID of the target site.
        tenant_id: UUID of the tenant.
        condition_type: Weather/traffic condition (normal, rain, strike ...).
        target_date: ISO-format date string (``YYYY-MM-DD``) or ``None``.
        algorithm: Clustering algorithm (dbscan, kmeans, hierarchical).
        eps_meters: DBSCAN neighbourhood radius.
        min_samples: DBSCAN minimum cluster size.
        n_clusters: Fixed cluster count for KMeans / hierarchical.
        max_cluster_size: Maximum employees per cluster (triggers splitting).
        max_walking_distance_meters: Meeting-zone walking constraint.
        max_route_duration_seconds: Maximum route duration.
        include_volunteers: Include volunteer-driver vehicles.
        use_osrm: Snap meeting zones via OSRM.

    Returns:
        A summary dict with ``optimization_id``, ``status``, and ``metrics``.
    """
    # Lazy imports to avoid circular dependencies at module level
    from sqlalchemy import select

    from app.database import async_session_factory
    from app.models.employee import Employee
    from app.models.leave import EmployeeLeave
    from app.models.optimization import Cluster as ClusterModel
    from app.models.optimization import Optimization, Route as RouteModel
    from app.models.site import Site
    from app.models.vehicle import Vehicle
    from app.services.clustering import EmployeePoint, run_clustering
    from app.services.vehicle_assignment import (
        AssignmentSummary,
        VehicleCandidate,
        assign_vehicles_to_clusters,
    )

    opt_id = uuid.UUID(optimization_id)
    s_id = uuid.UUID(site_id)
    t_id = uuid.UUID(tenant_id)
    t_date = date_type.fromisoformat(target_date) if target_date else None

    set_optimization_status(opt_id, "running", 0.0, "Loading data")
    logger.info("Optimization %s: starting pipeline for site %s", opt_id, s_id)

    try:
        async with async_session_factory() as session:
            async with session.begin():
                # ----------------------------------------------------------
                # Step 1 -- Load site (0 %)
                # ----------------------------------------------------------
                site_row = await session.get(Site, s_id)
                if site_row is None:
                    raise ValueError(f"Site {s_id} not found")

                # ----------------------------------------------------------
                # Step 2 -- Load employees for site (20 %)
                # ----------------------------------------------------------
                set_optimization_status(opt_id, "running", 0.2, "Loading employees")

                emp_q = (
                    select(Employee)
                    .where(
                        Employee.tenant_id == t_id,
                        Employee.site_id == s_id,
                        Employee.active.is_(True),
                        Employee.lat.isnot(None),
                        Employee.lng.isnot(None),
                    )
                )
                emp_result = await session.execute(emp_q)
                employees = list(emp_result.scalars().all())

                if not employees:
                    raise ValueError(
                        f"No geocoded active employees found for site {s_id}"
                    )

                # ----------------------------------------------------------
                # Step 2b -- Exclude employees on leave
                # ----------------------------------------------------------
                employees_on_leave: set[uuid.UUID] = set()
                if t_date is not None:
                    leave_q = (
                        select(EmployeeLeave.employee_id)
                        .where(
                            EmployeeLeave.start_date <= t_date,
                            EmployeeLeave.end_date >= t_date,
                        )
                    )
                    leave_result = await session.execute(leave_q)
                    employees_on_leave = {
                        row[0] for row in leave_result.all()
                    }

                active_employees = [
                    e for e in employees if e.id not in employees_on_leave
                ]
                excluded_leave_count = len(employees) - len(active_employees)

                if not active_employees:
                    raise ValueError(
                        "All employees are on leave for the target date"
                    )

                # ----------------------------------------------------------
                # Step 3 -- Load vehicles (40 %)
                # ----------------------------------------------------------
                set_optimization_status(opt_id, "running", 0.4, "Loading vehicles")

                veh_q = (
                    select(Vehicle)
                    .where(
                        Vehicle.tenant_id == t_id,
                        Vehicle.site_id == s_id,
                    )
                )
                veh_result = await session.execute(veh_q)
                vehicles_db = list(veh_result.scalars().all())

                # Build EmployeePoint list
                emp_points: list[EmployeePoint] = [
                    EmployeePoint(
                        employee_id=e.id,
                        lat=e.lat,  # type: ignore[arg-type]
                        lng=e.lng,  # type: ignore[arg-type]
                        is_pmr=e.is_pmr,
                    )
                    for e in active_employees
                ]

                # Build VehicleCandidate list
                fleet_candidates: list[VehicleCandidate] = [
                    VehicleCandidate(
                        vehicle_id=v.id,
                        capacity=v.capacity,
                        is_pmr_accessible=v.is_pmr_accessible,
                        zfe_compliant=v.zfe_compliant,
                        type=v.type,
                    )
                    for v in vehicles_db
                ]

                # Volunteer drivers (optional)
                volunteer_candidates: list[VehicleCandidate] = []
                if include_volunteers:
                    volunteer_emps = [
                        e
                        for e in active_employees
                        if e.volunteer_driver and e.carpool_seats > 0
                    ]
                    volunteer_candidates = [
                        VehicleCandidate(
                            vehicle_id=e.id,  # use employee id as proxy
                            capacity=e.carpool_seats,
                            is_pmr_accessible=False,
                            zfe_compliant=False,
                            type="Voiture",
                            is_volunteer=True,
                        )
                        for e in volunteer_emps
                    ]

                # ----------------------------------------------------------
                # Step 4 -- Run clustering (60 %)
                # ----------------------------------------------------------
                set_optimization_status(opt_id, "running", 0.6, "Running clustering")

                cluster_results = run_clustering(
                    employees=emp_points,
                    algorithm=algorithm,
                    eps_meters=eps_meters,
                    min_samples=min_samples,
                    n_clusters=n_clusters,
                    max_cluster_size=max_cluster_size,
                )

                # ----------------------------------------------------------
                # Step 5 -- Assign vehicles (80 %)
                # ----------------------------------------------------------
                set_optimization_status(
                    opt_id, "running", 0.8, "Assigning vehicles"
                )

                employee_locations: dict[uuid.UUID, tuple[float, float]] = {
                    e.id: (e.lat, e.lng)  # type: ignore[arg-type]
                    for e in active_employees
                }
                employee_pmr: dict[uuid.UUID, bool] = {
                    e.id: e.is_pmr for e in active_employees
                }

                assignment: AssignmentSummary = assign_vehicles_to_clusters(
                    clusters=cluster_results,
                    vehicles=fleet_candidates,
                    site_zfe=site_row.zfe_zone,
                    volunteer_drivers=volunteer_candidates if include_volunteers else None,
                    employee_locations=employee_locations,
                    employee_pmr=employee_pmr,
                )

                # ----------------------------------------------------------
                # Step 6 -- Persist results (90 %)
                # ----------------------------------------------------------
                set_optimization_status(opt_id, "running", 0.9, "Saving results")

                # Build metrics dict
                total_distance_km = 0.0
                total_duration_min = 0.0

                metrics = {
                    "total_employees": len(active_employees),
                    "employees_assigned": assignment.total_employees_assigned,
                    "employees_excluded_leave": excluded_leave_count,
                    "total_clusters": len(cluster_results),
                    "total_vehicles_used": assignment.total_vehicles_used,
                    "avg_occupancy_rate": round(
                        assignment.avg_occupancy_rate * 100, 1
                    ),
                    "total_distance_km": round(total_distance_km, 2),
                    "total_duration_minutes": round(total_duration_min, 2),
                    "unassigned_clusters": len(assignment.unassigned_clusters),
                }

                params = {
                    "algorithm": algorithm,
                    "eps_meters": eps_meters,
                    "min_samples": min_samples,
                    "n_clusters": n_clusters,
                    "max_cluster_size": max_cluster_size,
                    "max_walking_distance_meters": max_walking_distance_meters,
                    "max_route_duration_seconds": max_route_duration_seconds,
                    "include_volunteers": include_volunteers,
                    "use_osrm": use_osrm,
                }

                # Update the Optimization record
                opt_row = await session.get(Optimization, opt_id)
                if opt_row is None:
                    raise ValueError(
                        f"Optimization record {opt_id} not found"
                    )

                opt_row.status = "completed"
                opt_row.params = params
                opt_row.metrics = metrics
                opt_row.completed_at = datetime.now(timezone.utc)

                # Persist cluster records
                for idx, cr in enumerate(cluster_results):
                    cluster_rec = ClusterModel(
                        id=uuid.uuid4(),
                        optimization_id=opt_id,
                        site_id=s_id,
                        centroid_lat=cr.centroid_lat,
                        centroid_lng=cr.centroid_lng,
                        employee_count=cr.employee_count,
                        pmr_count=cr.pmr_count,
                        employee_ids=cr.employee_ids,
                    )
                    session.add(cluster_rec)

                # Persist assignment-based route stubs
                for asgn in assignment.assignments:
                    if asgn.vehicle_id is None:
                        continue
                    # Volunteer driver IDs are employee UUIDs, not
                    # real vehicle FKs -- store as None for now.
                    is_volunteer_vehicle = any(
                        vc.vehicle_id == asgn.vehicle_id and vc.is_volunteer
                        for vc in volunteer_candidates
                    )
                    route_rec = RouteModel(
                        id=uuid.uuid4(),
                        optimization_id=opt_id,
                        site_id=s_id,
                        vehicle_id=(
                            None if is_volunteer_vehicle else asgn.vehicle_id
                        ),
                        ordered_stops=[
                            str(eid) for eid in asgn.employee_ids
                        ],
                        total_distance_km=None,
                        total_time_minutes=None,
                    )
                    session.add(route_rec)

        # ----------------------------------------------------------
        # Done (100 %)
        # ----------------------------------------------------------
        set_optimization_status(opt_id, "completed", 1.0, "Done")
        logger.info(
            "Optimization %s completed: %d clusters, %d vehicles used",
            opt_id,
            len(cluster_results),
            assignment.total_vehicles_used,
        )

        return {
            "optimization_id": str(opt_id),
            "status": "completed",
            "metrics": metrics,
        }

    except Exception as exc:
        logger.exception("Optimization %s failed: %s", opt_id, exc)
        set_optimization_status(
            opt_id, "failed", 0.0, "Error", error=str(exc)
        )

        # Mark the DB record as failed
        try:
            async with async_session_factory() as session:
                async with session.begin():
                    opt_row = await session.get(Optimization, opt_id)
                    if opt_row is not None:
                        opt_row.status = "failed"
                        opt_row.metrics = {"error": str(exc)}
                        opt_row.completed_at = datetime.now(timezone.utc)
        except Exception:
            logger.exception(
                "Failed to mark optimization %s as failed in DB", opt_id
            )

        return {
            "optimization_id": str(opt_id),
            "status": "failed",
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Synchronous wrapper for Celery
# ---------------------------------------------------------------------------


def run_optimization_sync(
    optimization_id: str,
    site_id: str,
    tenant_id: str,
    **kwargs: object,
) -> dict:
    """Synchronous wrapper that runs the async pipeline in an event loop.

    This is intended to be called from a Celery worker or any synchronous
    context.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            run_optimization_task(
                optimization_id=optimization_id,
                site_id=site_id,
                tenant_id=tenant_id,
                **kwargs,  # type: ignore[arg-type]
            )
        )
    finally:
        loop.close()


# Register as a Celery task when the broker is available
if HAS_CELERY and celery_app is not None:
    optimize_pipeline_task = celery_app.task(
        name="transpop.optimize_pipeline",
        bind=False,
        queue="optimization",
        max_retries=1,
    )(run_optimization_sync)
