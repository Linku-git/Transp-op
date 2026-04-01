from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import date

from app.services.clustering import ClusterResult, EmployeePoint, run_clustering
from app.services.meeting_zones import MeetingZone, optimize_meeting_zones
from app.services.routing import RoutingResult, optimize_routes
from app.services.vehicle_assignment import (
    AssignmentResult,
    AssignmentSummary,
    VehicleCandidate,
    assign_vehicles_to_clusters,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PipelineParams:
    """Input parameters for the optimization pipeline."""

    site_id: uuid.UUID
    tenant_id: uuid.UUID
    condition_type: str = "normal"
    target_date: date | None = None
    algorithm: str = "dbscan"
    eps_meters: float = 500.0
    min_samples: int = 2
    n_clusters: int | None = None
    max_cluster_size: int | None = None
    max_walking_distance_meters: float = 800.0
    max_route_duration_seconds: int = 5400
    include_volunteers: bool = False
    use_osrm: bool = True


@dataclass
class PipelineMetrics:
    """Computed metrics from the optimization run."""

    total_employees: int = 0
    employees_assigned: int = 0
    employees_excluded_leave: int = 0
    total_clusters: int = 0
    total_vehicles_used: int = 0
    avg_occupancy_rate: float = 0.0
    total_distance_km: float = 0.0
    total_duration_minutes: float = 0.0
    estimated_fuel_liters: float = 0.0
    estimated_fuel_cost_mad: float = 0.0
    co2_estimate_kg: float = 0.0
    time_saved_vs_individual_hours: float = 0.0
    unassigned_clusters: int = 0


@dataclass
class PipelineResult:
    """Full output of the optimization pipeline."""

    optimization_id: uuid.UUID | None = None
    params: PipelineParams | None = None
    metrics: PipelineMetrics | None = None
    clusters: list[ClusterResult] | None = None
    assignments: list[AssignmentResult] | None = None
    routing: RoutingResult | None = None
    meeting_zones: list[MeetingZone] | None = None
    status: str = "pending"
    error: str | None = None


# ---------------------------------------------------------------------------
# Metrics calculation (pure function)
# ---------------------------------------------------------------------------


def calculate_metrics(
    total_employees: int,
    employees_excluded: int,
    clusters: list[ClusterResult],
    assignment_summary: AssignmentSummary,
    routing_result: RoutingResult,
    fuel_cost_per_liter: float = 12.0,
    avg_fuel_consumption_l_per_100km: float = 15.0,
    co2_per_liter_diesel: float = 2.68,
    avg_individual_commute_minutes: float = 45.0,
) -> PipelineMetrics:
    """Compute aggregate metrics from the optimization outputs.

    Args:
        total_employees: Total employees before filtering.
        employees_excluded: Employees excluded (on leave, missing coords).
        clusters: Cluster results from the clustering step.
        assignment_summary: Vehicle assignment summary.
        routing_result: Route optimization result.
        fuel_cost_per_liter: Cost of diesel in MAD per liter.
        avg_fuel_consumption_l_per_100km: Average fuel consumption for buses.
        co2_per_liter_diesel: kg of CO2 emitted per liter of diesel.
        avg_individual_commute_minutes: Average one-way commute if driving alone.

    Returns:
        PipelineMetrics with all computed values.
    """
    total_distance_km = routing_result.total_distance_km
    total_duration_minutes = routing_result.total_duration_minutes
    employees_assigned = assignment_summary.total_employees_assigned

    estimated_fuel_liters = total_distance_km * avg_fuel_consumption_l_per_100km / 100.0
    estimated_fuel_cost_mad = estimated_fuel_liters * fuel_cost_per_liter
    co2_estimate_kg = estimated_fuel_liters * co2_per_liter_diesel

    # Time saved: compare pooled transport vs. every employee driving alone
    # (round-trip: multiply individual commute by 2)
    individual_total_minutes = employees_assigned * avg_individual_commute_minutes * 2.0
    time_saved_minutes = individual_total_minutes - total_duration_minutes
    time_saved_vs_individual_hours = max(time_saved_minutes / 60.0, 0.0)

    return PipelineMetrics(
        total_employees=total_employees,
        employees_assigned=employees_assigned,
        employees_excluded_leave=employees_excluded,
        total_clusters=len(clusters),
        total_vehicles_used=assignment_summary.total_vehicles_used,
        avg_occupancy_rate=assignment_summary.avg_occupancy_rate,
        total_distance_km=total_distance_km,
        total_duration_minutes=total_duration_minutes,
        estimated_fuel_liters=round(estimated_fuel_liters, 2),
        estimated_fuel_cost_mad=round(estimated_fuel_cost_mad, 2),
        co2_estimate_kg=round(co2_estimate_kg, 2),
        time_saved_vs_individual_hours=round(time_saved_vs_individual_hours, 2),
        unassigned_clusters=len(assignment_summary.unassigned_clusters),
    )


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------


async def run_optimization_pipeline(
    params: PipelineParams,
    employees: list[EmployeePoint],
    employee_leave_ids: set[uuid.UUID],
    vehicles: list[VehicleCandidate],
    volunteer_drivers: list[VehicleCandidate],
    site_lat: float,
    site_lng: float,
    site_zfe: bool,
    employee_locations: dict[uuid.UUID, tuple[float, float]],
    employee_pmr: dict[uuid.UUID, bool],
) -> PipelineResult:
    """Run the full optimization pipeline: cluster -> zones -> assign -> route.

    Args:
        params: Pipeline configuration parameters.
        employees: All eligible employees with coordinates.
        employee_leave_ids: Set of employee IDs currently on leave.
        vehicles: Fleet vehicles available for assignment.
        volunteer_drivers: Personal-vehicle volunteers (used if include_volunteers).
        site_lat: Latitude of the destination site.
        site_lng: Longitude of the destination site.
        site_zfe: Whether the site is inside a low-emission zone (ZFE).
        employee_locations: Mapping of employee_id -> (lat, lng).
        employee_pmr: Mapping of employee_id -> is_pmr flag.

    Returns:
        PipelineResult containing all outputs and metrics.
    """
    optimization_id = uuid.uuid4()
    result = PipelineResult(
        optimization_id=optimization_id,
        params=params,
        status="running",
    )

    total_employees_before = len(employees)

    # ------------------------------------------------------------------
    # Step 1: Filter employees on leave
    # ------------------------------------------------------------------
    active_employees = [
        emp for emp in employees if emp.employee_id not in employee_leave_ids
    ]
    employees_excluded = total_employees_before - len(active_employees)

    logger.info(
        "Pipeline %s: %d employees total, %d excluded (on leave), %d active",
        optimization_id,
        total_employees_before,
        employees_excluded,
        len(active_employees),
    )

    # ------------------------------------------------------------------
    # Step 2: Validate minimum employee count
    # ------------------------------------------------------------------
    if len(active_employees) < 2:
        result.status = "failed"
        result.error = (
            f"Insufficient employees for optimization: {len(active_employees)} "
            f"active (need at least 2). {employees_excluded} excluded due to leave."
        )
        logger.warning("Pipeline %s: %s", optimization_id, result.error)
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
        )
        return result

    # Also filter employee_locations and employee_pmr to active only
    active_ids = {emp.employee_id for emp in active_employees}
    active_locations = {
        eid: loc for eid, loc in employee_locations.items() if eid in active_ids
    }
    active_pmr = {
        eid: pmr for eid, pmr in employee_pmr.items() if eid in active_ids
    }

    # ------------------------------------------------------------------
    # Step 3: Clustering
    # ------------------------------------------------------------------
    try:
        clusters = run_clustering(
            employees=active_employees,
            algorithm=params.algorithm,
            eps_meters=params.eps_meters,
            min_samples=params.min_samples,
            n_clusters=params.n_clusters,
            max_cluster_size=params.max_cluster_size,
        )
        result.clusters = clusters
        logger.info(
            "Pipeline %s: clustering produced %d clusters",
            optimization_id,
            len(clusters),
        )
    except Exception:
        logger.exception("Pipeline %s: clustering failed", optimization_id)
        result.status = "failed"
        result.error = "Clustering step failed. Check logs for details."
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
        )
        return result

    if not clusters:
        result.status = "failed"
        result.error = "Clustering produced zero clusters."
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
        )
        return result

    # ------------------------------------------------------------------
    # Step 4: Meeting zones
    # ------------------------------------------------------------------
    try:
        meeting_zones = await optimize_meeting_zones(
            clusters=clusters,
            employees=active_employees,
            max_walking_distance_meters=params.max_walking_distance_meters,
            use_osrm=params.use_osrm,
        )
        result.meeting_zones = meeting_zones
        logger.info(
            "Pipeline %s: computed %d meeting zones",
            optimization_id,
            len(meeting_zones),
        )
    except Exception:
        logger.exception("Pipeline %s: meeting zone optimization failed", optimization_id)
        # Meeting zones are non-critical; continue with cluster centroids
        result.meeting_zones = []
        logger.info(
            "Pipeline %s: continuing without meeting zones (using cluster centroids)",
            optimization_id,
        )

    # ------------------------------------------------------------------
    # Step 5: Vehicle assignment
    # ------------------------------------------------------------------
    try:
        effective_volunteers = volunteer_drivers if params.include_volunteers else []
        assignment_summary = assign_vehicles_to_clusters(
            clusters=clusters,
            vehicles=vehicles,
            site_zfe=site_zfe,
            volunteer_drivers=effective_volunteers or None,
            employee_locations=active_locations or None,
            employee_pmr=active_pmr or None,
        )
        result.assignments = assignment_summary.assignments
        logger.info(
            "Pipeline %s: assigned %d vehicles to %d clusters, "
            "%d unassigned clusters",
            optimization_id,
            assignment_summary.total_vehicles_used,
            len(clusters),
            len(assignment_summary.unassigned_clusters),
        )
    except Exception:
        logger.exception("Pipeline %s: vehicle assignment failed", optimization_id)
        result.status = "failed"
        result.error = "Vehicle assignment step failed. Check logs for details."
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
            total_clusters=len(clusters),
        )
        return result

    # ------------------------------------------------------------------
    # Step 6: Route optimization
    # ------------------------------------------------------------------
    try:
        routing_result = await optimize_routes(
            clusters=clusters,
            assignments=assignment_summary.assignments,
            site_lat=site_lat,
            site_lng=site_lng,
            employee_locations=active_locations,
            use_osrm=params.use_osrm,
            max_route_duration_seconds=params.max_route_duration_seconds,
        )
        result.routing = routing_result
        logger.info(
            "Pipeline %s: routing complete — %.1f km, %.1f min, %d routes",
            optimization_id,
            routing_result.total_distance_km,
            routing_result.total_duration_minutes,
            len(routing_result.routes),
        )
    except Exception:
        logger.exception("Pipeline %s: route optimization failed", optimization_id)
        result.status = "failed"
        result.error = "Route optimization step failed. Check logs for details."
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
            total_clusters=len(clusters),
            total_vehicles_used=assignment_summary.total_vehicles_used,
            unassigned_clusters=len(assignment_summary.unassigned_clusters),
        )
        return result

    # ------------------------------------------------------------------
    # Step 7: Calculate metrics
    # ------------------------------------------------------------------
    try:
        metrics = calculate_metrics(
            total_employees=total_employees_before,
            employees_excluded=employees_excluded,
            clusters=clusters,
            assignment_summary=assignment_summary,
            routing_result=routing_result,
        )
        result.metrics = metrics
    except Exception:
        logger.exception("Pipeline %s: metrics calculation failed", optimization_id)
        # Populate partial metrics even if calculation fails
        result.metrics = PipelineMetrics(
            total_employees=total_employees_before,
            employees_excluded_leave=employees_excluded,
            total_clusters=len(clusters),
            total_vehicles_used=assignment_summary.total_vehicles_used,
            total_distance_km=routing_result.total_distance_km,
            total_duration_minutes=routing_result.total_duration_minutes,
            unassigned_clusters=len(assignment_summary.unassigned_clusters),
        )

    result.status = "completed"
    logger.info(
        "Pipeline %s: completed — %d employees assigned, %d vehicles, "
        "%.1f km total, %.1f min total, %.2f kg CO2",
        optimization_id,
        result.metrics.employees_assigned,
        result.metrics.total_vehicles_used,
        result.metrics.total_distance_km,
        result.metrics.total_duration_minutes,
        result.metrics.co2_estimate_kg,
    )
    return result
