from __future__ import annotations

import logging
import math
import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.configuration_plan import ConfigurationPlan
from app.models.configuration_transport import ConfigurationTransport
from app.models.point_arret import PointArret
from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transport-optimization")

# ── vehicle capacity assumptions ────────────────────────────────────────────
CAPACITY: dict[str, int] = {
    "AUTOCAR": 54,
    "MINIBUS":  25,
    "MINICAR":  12,
}
# Cost per km in MAD (rough)
COST_PER_KM: dict[str, float] = {
    "AUTOCAR": 4.50,
    "MINIBUS": 3.20,
    "MINICAR": 2.50,
}
# Minimum fill ratio to avoid sending an unnecessarily large vehicle
MIN_FILL = 0.70


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA MODELS
# ═══════════════════════════════════════════════════════════════════════════

class StopStat(BaseModel):
    id: str
    code: str
    nom: str
    ville: str | None
    lat: float | None
    lng: float | None
    prestataire: str | None
    is_active: bool
    usage_count: int          # how many config_transport rows reference this stop area
    utilization_score: float  # 0-100, derived from usage_count relative to avg
    walking_score: float      # 0-100, mock score based on city coverage density
    coverage_radius_m: int    # estimated coverage area in meters

class StopsAnalysisResponse(BaseModel):
    total_stops: int
    active_stops: int
    cities: list[dict[str, Any]]
    stops: list[StopStat]
    avg_usage: float
    coverage_pct: float       # % of config routes covered by mapped stops

class TripItem(BaseModel):
    id: str
    poste: str | None
    conducteur: str | None
    shift: str | None
    aller_retour: str | None
    secteur: str | None
    entite: str | None
    prestataire: str | None
    type_vehicule: str | None
    mle_vehicule: str | None
    heure_depart: str | None
    heure_arrivee: str | None
    point_depart: str | None
    point_arrivee: str | None
    arrets_circuit: str | None
    km: float | None
    rot: float | None
    t_km: float | None
    duree_trajet_min: int | None
    # enriched
    capacity: int
    estimated_passengers: int
    fill_pct: float
    stops_list: list[str]
    estimated_cost_mad: float

class TripsListResponse(BaseModel):
    plan_id: str
    plan_name: str
    total: int
    trips: list[TripItem]

class TripDetailResponse(BaseModel):
    trip: TripItem
    # Map data
    start_point: dict[str, Any] | None    # {lat, lng, label}
    end_point: dict[str, Any] | None
    waypoints: list[dict[str, Any]]       # [{lat, lng, label, code}]
    google_maps_url: str

class FleetAnalysis(BaseModel):
    plan_id: str
    plan_name: str
    total_trips: int
    total_postes: int
    total_km: float
    total_tkm: float
    shifts: dict[str, int]
    vehicle_dist: dict[str, int]
    secteurs: dict[str, int]
    avg_fill_pct: float
    routes_below_70: int
    routes_above_100: int
    estimated_daily_cost_mad: float
    current_score: dict[str, float]   # {efficiency, finance, fill, co2}

class OptimizedTrip(BaseModel):
    trip_id: str
    poste: str | None
    shift: str | None
    aller_retour: str | None
    current_vehicle: str | None
    suggested_vehicle: str | None
    current_capacity: int
    suggested_capacity: int
    estimated_passengers: int
    current_fill_pct: float
    suggested_fill_pct: float
    current_cost: float
    suggested_cost: float
    saving_mad: float
    action: str   # "downsize" | "upsize" | "keep" | "merge_candidate"

class OptimizationResult(BaseModel):
    plan_id: str
    total_trips: int
    trips_optimized: int
    trips_kept: int
    trips_downsized: int
    trips_upsized: int
    total_saving_mad: float
    total_saving_pct: float
    fill_improvement_pct: float
    new_score: dict[str, float]
    optimized_trips: list[OptimizedTrip]
    summary: str
    can_generate_plan: bool


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _parse_stops(arrets: str | None) -> list[str]:
    if not arrets:
        return []
    import re
    # split on common separators: -, >, ,, /
    parts = re.split(r'[-]{1,4}|>{1,4}|[,/]', arrets)
    return [p.strip() for p in parts if p.strip()]


def _estimate_passengers(type_veh: str | None, fill_assumption: float = 0.82) -> int:
    cap = CAPACITY.get(type_veh or "", 25)
    return max(1, round(cap * fill_assumption))


def _fill_pct(passengers: int, type_veh: str | None) -> float:
    cap = CAPACITY.get(type_veh or "", 25)
    return round(passengers / cap * 100, 1)


def _trip_daily_cost(t: ConfigurationTransport) -> float:
    km = float(t.km or 0)
    rot = float(t.rot or 1)
    cpm = COST_PER_KM.get(t.type_vehicule or "", 3.50)
    return km * rot * cpm


def _to_trip_item(t: ConfigurationTransport, fill_assumption: float = 0.82) -> TripItem:
    est_pass = _estimate_passengers(t.type_vehicule, fill_assumption)
    cap = CAPACITY.get(t.type_vehicule or "", 25)
    return TripItem(
        id=str(t.id),
        poste=t.poste,
        conducteur=t.conducteur,
        shift=t.shift,
        aller_retour=t.aller_retour,
        secteur=t.secteur,
        entite=t.entite,
        prestataire=t.prestataire,
        type_vehicule=t.type_vehicule,
        mle_vehicule=t.mle_vehicule,
        heure_depart=t.heure_depart,
        heure_arrivee=t.heure_arrivee,
        point_depart=t.point_depart,
        point_arrivee=t.point_arrivee,
        arrets_circuit=t.arrets_circuit,
        km=float(t.km) if t.km is not None else None,
        rot=float(t.rot) if t.rot is not None else None,
        t_km=float(t.t_km) if t.t_km is not None else None,
        duree_trajet_min=t.duree_trajet_min,
        capacity=cap,
        estimated_passengers=est_pass,
        fill_pct=_fill_pct(est_pass, t.type_vehicule),
        stops_list=_parse_stops(t.arrets_circuit),
        estimated_cost_mad=round(_trip_daily_cost(t), 2),
    )


def _score_config(trips: list[ConfigurationTransport]) -> dict[str, float]:
    if not trips:
        return {"efficiency": 0, "finance": 0, "fill": 0, "co2": 0}
    fills = []
    for t in trips:
        est = _estimate_passengers(t.type_vehicule)
        cap = CAPACITY.get(t.type_vehicule or "", 25)
        fills.append(est / cap)
    avg_fill = sum(fills) / len(fills) * 100
    # Finance score: lower total cost per km is better
    total_cost = sum(_trip_daily_cost(t) for t in trips)
    total_km = sum(float(t.km or 0) * float(t.rot or 1) for t in trips)
    cost_per_km = total_cost / total_km if total_km > 0 else 4.5
    finance_score = max(0, 100 - (cost_per_km - 2.0) * 20)
    # CO2 score (lower is better: 80% of trips with correct vehicle → higher score)
    over_cap = sum(1 for f in fills if f < MIN_FILL)
    co2_score = max(0, 100 - (over_cap / len(fills)) * 100)
    # Efficiency: unique postes / total trips
    postes = len(set(t.poste for t in trips if t.poste))
    eff_score = min(100, postes / len(trips) * 200)
    return {
        "efficiency": round(eff_score, 1),
        "finance": round(finance_score, 1),
        "fill": round(avg_fill, 1),
        "co2": round(co2_score, 1),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: Stops Analysis
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/stops", response_model=StopsAnalysisResponse)
async def get_stops_analysis(
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> StopsAnalysisResponse:
    """Return all points d'arrêt enriched with usage stats and coverage scores."""
    # Load all stops
    stops_stmt = select(PointArret).where(
        PointArret.tenant_id == current_user.tenant_id
    ).order_by(PointArret.ville, PointArret.nom)
    stops_result = await db.execute(stops_stmt)
    stops = list(stops_result.scalars().all())

    if not stops:
        return StopsAnalysisResponse(
            total_stops=0, active_stops=0, cities=[], stops=[],
            avg_usage=0, coverage_pct=0,
        )

    # Load all point_depart / point_arrivee from current plan for usage mapping
    config_stmt = select(
        ConfigurationTransport.point_depart,
        ConfigurationTransport.point_arrivee,
        ConfigurationTransport.arrets_circuit,
        ConfigurationTransport.secteur,
    ).where(ConfigurationTransport.tenant_id == current_user.tenant_id)
    config_result = await db.execute(config_stmt)
    config_rows = config_result.fetchall()

    # Build usage map: how many config trips reference each city/sector
    city_usage: dict[str, int] = {}
    total_config = len(config_rows)
    for row in config_rows:
        for field in [row.point_depart, row.point_arrivee]:
            if field:
                norm = field.upper().strip()
                city_usage[norm] = city_usage.get(norm, 0) + 1

    # Assign usage_count per stop based on city name match
    def stop_usage(stop: PointArret) -> int:
        if not stop.ville:
            return 0
        city_upper = stop.ville.upper()
        base = sum(v for k, v in city_usage.items() if city_upper in k or k in city_upper)
        return base

    # Compute avg usage
    usage_counts = [stop_usage(s) for s in stops]
    avg_usage = sum(usage_counts) / len(usage_counts) if usage_counts else 1

    # Build city distribution
    city_map: dict[str, dict[str, Any]] = {}
    for s in stops:
        city = s.ville or "Inconnu"
        if city not in city_map:
            city_map[city] = {"name": city, "count": 0, "active": 0}
        city_map[city]["count"] += 1
        if s.is_active:
            city_map[city]["active"] += 1

    # Walking score: based on stop density in city (more stops per city → better coverage → lower per-stop score but higher city score)
    # Using a simple formula based on distance to nearest neighbor
    def walking_score(stop: PointArret, all_stops: list[PointArret]) -> float:
        if stop.lat is None or stop.lng is None:
            return 50.0
        same_city = [s for s in all_stops if s.ville == stop.ville and s.id != stop.id and s.lat and s.lng]
        if not same_city:
            return 70.0
        min_dist = min(_haversine_km(stop.lat, stop.lng, s.lat, s.lng) for s in same_city) * 1000
        # < 300m → 90+, 300-600m → 70-90, 600-1000m → 50-70, >1000m → <50
        if min_dist < 300:
            return min(98, 90 + (300 - min_dist) / 300 * 8)
        elif min_dist < 600:
            return 70 + (600 - min_dist) / 300 * 20
        elif min_dist < 1000:
            return 50 + (1000 - min_dist) / 400 * 20
        else:
            return max(20, 50 - (min_dist - 1000) / 1000 * 30)

    stop_stats: list[StopStat] = []
    for i, stop in enumerate(stops):
        u = usage_counts[i]
        util_score = min(100.0, (u / avg_usage) * 60) if avg_usage > 0 else 50.0
        w_score = walking_score(stop, stops)
        stop_stats.append(StopStat(
            id=str(stop.id),
            code=stop.code or "",
            nom=stop.nom or "",
            ville=stop.ville,
            lat=stop.lat,
            lng=stop.lng,
            prestataire=stop.prestataire,
            is_active=stop.is_active or False,
            usage_count=u,
            utilization_score=round(util_score, 1),
            walking_score=round(w_score, 1),
            coverage_radius_m=int(min(800, max(200, avg_usage * 15))),
        ))

    covered_cities = set(s.ville for s in stops if s.is_active and s.ville)
    config_cities = set()
    for row in config_rows:
        for field in [row.point_depart, row.point_arrivee]:
            if field:
                for city in covered_cities:
                    if city and city.upper() in field.upper():
                        config_cities.add(city)
    coverage_pct = (len(config_cities) / max(1, len(covered_cities))) * 100 if covered_cities else 0

    return StopsAnalysisResponse(
        total_stops=len(stops),
        active_stops=sum(1 for s in stops if s.is_active),
        cities=list(city_map.values()),
        stops=stop_stats,
        avg_usage=round(avg_usage, 1),
        coverage_pct=round(coverage_pct, 1),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: Fleet Analysis (current state)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/plan/{plan_id}/analysis", response_model=FleetAnalysis)
async def get_fleet_analysis(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> FleetAnalysis:
    """Analyze current fleet configuration for a plan."""
    plan_stmt = select(ConfigurationPlan).where(
        ConfigurationPlan.id == plan_id,
        ConfigurationPlan.tenant_id == current_user.tenant_id,
    )
    plan_result = await db.execute(plan_stmt)
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    trips_stmt = select(ConfigurationTransport).where(
        ConfigurationTransport.plan_id == plan_id,
        ConfigurationTransport.tenant_id == current_user.tenant_id,
    )
    trips_result = await db.execute(trips_stmt)
    trips = list(trips_result.scalars().all())

    if not trips:
        raise HTTPException(status_code=404, detail="No trips in this plan")

    shifts: dict[str, int] = {}
    vehicle_dist: dict[str, int] = {}
    secteurs: dict[str, int] = {}
    total_km = 0.0
    total_tkm = 0.0
    fills = []
    daily_cost = 0.0

    for t in trips:
        if t.shift:
            shifts[t.shift] = shifts.get(t.shift, 0) + 1
        vtype = t.type_vehicule or "UNKNOWN"
        vehicle_dist[vtype] = vehicle_dist.get(vtype, 0) + 1
        if t.secteur:
            secteurs[t.secteur] = secteurs.get(t.secteur, 0) + 1
        total_km += float(t.km or 0)
        total_tkm += float(t.t_km or 0)
        est = _estimate_passengers(t.type_vehicule)
        cap = CAPACITY.get(t.type_vehicule or "", 25)
        fills.append(est / cap)
        daily_cost += _trip_daily_cost(t)

    avg_fill = sum(fills) / len(fills) * 100 if fills else 0
    routes_below = sum(1 for f in fills if f < MIN_FILL)
    routes_above = sum(1 for f in fills if f > 1.0)
    postes = len(set(t.poste for t in trips if t.poste))
    score = _score_config(trips)

    return FleetAnalysis(
        plan_id=str(plan_id),
        plan_name=plan.name,
        total_trips=len(trips),
        total_postes=postes,
        total_km=round(total_km, 1),
        total_tkm=round(total_tkm, 1),
        shifts=shifts,
        vehicle_dist=vehicle_dist,
        secteurs=secteurs,
        avg_fill_pct=round(avg_fill, 1),
        routes_below_70=routes_below,
        routes_above_100=routes_above,
        estimated_daily_cost_mad=round(daily_cost, 0),
        current_score=score,
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: Fleet Optimizer (VRP-lite with capacity constraints)
# ═══════════════════════════════════════════════════════════════════════════

class OptimizeParams(BaseModel):
    min_fill_rate: float = 0.70
    fill_assumption: float = 0.82
    prefer_smaller: bool = True
    shift_filter: str | None = None
    secteur_filter: str | None = None

@router.post("/plan/{plan_id}/optimize", response_model=OptimizationResult)
async def optimize_fleet(
    plan_id: uuid.UUID,
    params: OptimizeParams,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> OptimizationResult:
    """Run VRP-lite fleet optimizer: reassign vehicle types to meet ≥70% fill constraint."""
    plan_stmt = select(ConfigurationPlan).where(
        ConfigurationPlan.id == plan_id,
        ConfigurationPlan.tenant_id == current_user.tenant_id,
    )
    plan_result = await db.execute(plan_stmt)
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    trips_stmt = select(ConfigurationTransport).where(
        ConfigurationTransport.plan_id == plan_id,
        ConfigurationTransport.tenant_id == current_user.tenant_id,
    )
    if params.shift_filter:
        trips_stmt = trips_stmt.where(ConfigurationTransport.shift == params.shift_filter)
    if params.secteur_filter:
        trips_stmt = trips_stmt.where(ConfigurationTransport.secteur == params.secteur_filter)

    trips_result = await db.execute(trips_stmt)
    trips = list(trips_result.scalars().all())

    if not trips:
        raise HTTPException(status_code=404, detail="No trips match the given filters")

    VEH_ORDER = ["MINICAR", "MINIBUS", "AUTOCAR"]  # ascending capacity

    optimized: list[OptimizedTrip] = []
    kept = downsized = upsized = 0
    total_saving = 0.0
    old_fills = []
    new_fills = []

    for t in trips:
        curr_veh = t.type_vehicule or "MINIBUS"
        curr_cap = CAPACITY.get(curr_veh, 25)
        est_pass = max(1, round(curr_cap * params.fill_assumption))
        curr_fill = est_pass / curr_cap
        old_fills.append(curr_fill)

        curr_cost = _trip_daily_cost(t)
        cpm_curr = COST_PER_KM.get(curr_veh, 3.5)

        # Find best vehicle: smallest that achieves ≥ min_fill_rate and fits all passengers
        best_veh = curr_veh
        best_action = "keep"

        if params.prefer_smaller:
            for vtype in VEH_ORDER:
                vcap = CAPACITY[vtype]
                if vcap >= est_pass:
                    fill = est_pass / vcap
                    if fill >= params.min_fill_rate:
                        best_veh = vtype
                        break
            else:
                # Can't fit with min fill → use current
                best_veh = curr_veh
        else:
            # Only upsize if needed
            best_veh = curr_veh

        best_cap = CAPACITY[best_veh]
        best_fill = est_pass / best_cap
        new_fills.append(best_fill)

        km_val = float(t.km or 0)
        rot_val = float(t.rot or 1)
        new_cost = km_val * rot_val * COST_PER_KM[best_veh]
        saving = curr_cost - new_cost

        if best_veh == curr_veh:
            best_action = "keep"
        elif VEH_ORDER.index(best_veh) < VEH_ORDER.index(curr_veh):
            best_action = "downsize"
            downsized += 1
        else:
            best_action = "upsize"
            upsized += 1

        if best_action != "keep":
            total_saving += saving
        else:
            kept += 1

        optimized.append(OptimizedTrip(
            trip_id=str(t.id),
            poste=t.poste,
            shift=t.shift,
            aller_retour=t.aller_retour,
            current_vehicle=curr_veh,
            suggested_vehicle=best_veh,
            current_capacity=curr_cap,
            suggested_capacity=best_cap,
            estimated_passengers=est_pass,
            current_fill_pct=round(curr_fill * 100, 1),
            suggested_fill_pct=round(best_fill * 100, 1),
            current_cost=round(curr_cost, 2),
            suggested_cost=round(new_cost, 2),
            saving_mad=round(saving, 2),
            action=best_action,
        ))

    total_curr_cost = sum(o.current_cost for o in optimized)
    saving_pct = (total_saving / total_curr_cost * 100) if total_curr_cost > 0 else 0
    avg_old_fill = sum(old_fills) / len(old_fills) * 100 if old_fills else 0
    avg_new_fill = sum(new_fills) / len(new_fills) * 100 if new_fills else 0
    fill_improvement = avg_new_fill - avg_old_fill
    trips_optimized = downsized + upsized

    # Build scores
    new_trips_mock = []
    for t, o in zip(trips, optimized):
        # simulate new type
        t_copy_type = o.suggested_vehicle
        # use original trip for km/rot
        pass
    new_eff = min(100, _score_config(trips)["efficiency"])
    new_finance = min(100, 100 - ((total_curr_cost - total_saving) / max(1, total_curr_cost)) * 100 + 10)
    new_fill = avg_new_fill
    new_co2 = min(100, 100 - sum(1 for f in new_fills if f < MIN_FILL) / len(new_fills) * 100)

    summary_parts = []
    if downsized > 0:
        summary_parts.append(f"{downsized} trajets réduits (plus petit véhicule)")
    if upsized > 0:
        summary_parts.append(f"{upsized} trajets agrandis (plus grand véhicule)")
    if kept > 0 and trips_optimized == 0:
        summary_parts.append("Configuration déjà optimale")
    elif kept > 0:
        summary_parts.append(f"{kept} trajets inchangés")

    return OptimizationResult(
        plan_id=str(plan_id),
        total_trips=len(trips),
        trips_optimized=trips_optimized,
        trips_kept=kept,
        trips_downsized=downsized,
        trips_upsized=upsized,
        total_saving_mad=round(total_saving, 0),
        total_saving_pct=round(saving_pct, 1),
        fill_improvement_pct=round(fill_improvement, 1),
        new_score={
            "efficiency": round(new_eff, 1),
            "finance": round(new_finance, 1),
            "fill": round(new_fill, 1),
            "co2": round(new_co2, 1),
        },
        optimized_trips=optimized,
        summary=" · ".join(summary_parts) or "Aucune modification recommandée",
        can_generate_plan=trips_optimized > 0,
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 4: Trips list for route viewer
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/plan/{plan_id}/trips", response_model=TripsListResponse)
async def get_plan_trips(
    plan_id: uuid.UUID,
    shift: str | None = Query(default=None),
    aller_retour: str | None = Query(default=None),
    secteur: str | None = Query(default=None),
    prestataire: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> TripsListResponse:
    """Return all trips in a plan for the route viewer."""
    plan_stmt = select(ConfigurationPlan).where(
        ConfigurationPlan.id == plan_id,
        ConfigurationPlan.tenant_id == current_user.tenant_id,
    )
    plan_result = await db.execute(plan_stmt)
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    stmt = select(ConfigurationTransport).where(
        ConfigurationTransport.plan_id == plan_id,
        ConfigurationTransport.tenant_id == current_user.tenant_id,
    )
    if shift:
        stmt = stmt.where(ConfigurationTransport.shift == shift)
    if aller_retour:
        stmt = stmt.where(ConfigurationTransport.aller_retour == aller_retour)
    if secteur:
        stmt = stmt.where(ConfigurationTransport.secteur == secteur)
    if prestataire:
        stmt = stmt.where(ConfigurationTransport.prestataire == prestataire)

    stmt = stmt.order_by(
        ConfigurationTransport.shift,
        ConfigurationTransport.poste,
        ConfigurationTransport.aller_retour,
    )

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Paginate
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    trips_result = await db.execute(stmt)
    trips = list(trips_result.scalars().all())

    return TripsListResponse(
        plan_id=str(plan_id),
        plan_name=plan.name,
        total=total,
        trips=[_to_trip_item(t) for t in trips],
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINT 5: Trip detail with map coordinates
# ═══════════════════════════════════════════════════════════════════════════

# Known Khouribga area coordinates for common location names
KNOWN_COORDS: dict[str, tuple[float, float]] = {
    "KHOURIBGA": (32.886, -6.907),
    "OUED ZEM": (32.863, -6.574),
    "OUEDZEM": (32.863, -6.574),
    "BOUJNIBA": (32.633, -6.983),
    "HATTANE": (32.750, -6.930),
    "FQUIH BEN SALEH": (32.500, -6.687),
    "BOULANOIR": (32.696, -7.038),
    "BENI AMIR MINE": (32.990, -6.985),
    "DAOUI": (32.920, -6.840),
    "MERA": (32.940, -6.800),
    "GROUNI": (32.850, -6.750),
    "LAVERIE MERA": (32.935, -6.798),
    "STEP": (32.895, -6.910),
    "PIPE LINE": (32.940, -6.780),
    "COZ": (32.860, -6.560),
    "RECETTE 6": (32.620, -6.990),
    "UB-UM3": (32.990, -6.960),
    "ZONE CENTRALE": (32.980, -6.975),
}

def _resolve_coord(name: str | None, stops: list[PointArret]) -> tuple[float, float] | None:
    if not name:
        return None
    name_upper = name.upper().strip()
    # Try point_arret match
    for s in stops:
        if s.nom and s.nom.upper() in name_upper:
            if s.lat and s.lng:
                return (s.lat, s.lng)
        if s.code and s.code.upper() in name_upper:
            if s.lat and s.lng:
                return (s.lat, s.lng)
    # Try known coords
    for k, v in KNOWN_COORDS.items():
        if k in name_upper or name_upper in k:
            return v
    return None


def _google_maps_url(start: str | None, end: str | None, waypoints: list[str]) -> str:
    base = "https://www.google.com/maps/dir/"
    parts = []
    if start:
        parts.append(f"{start},+Morocco")
    for wp in waypoints[:8]:  # Google Maps limits to 8 waypoints on URL
        parts.append(f"{wp},+Morocco")
    if end:
        parts.append(f"{end},+Morocco")
    return base + "/".join(p.replace(" ", "+") for p in parts)


@router.get("/trip/{trip_id}", response_model=TripDetailResponse)
async def get_trip_detail(
    trip_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> TripDetailResponse:
    """Return full trip detail with coordinates for map visualization."""
    trip_stmt = select(ConfigurationTransport).where(
        ConfigurationTransport.id == trip_id,
        ConfigurationTransport.tenant_id == current_user.tenant_id,
    )
    trip_result = await db.execute(trip_stmt)
    trip = trip_result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Load all stops for coordinate resolution
    stops_stmt = select(PointArret).where(
        PointArret.tenant_id == current_user.tenant_id
    )
    stops_result = await db.execute(stops_stmt)
    all_stops = list(stops_result.scalars().all())

    start_coord = _resolve_coord(trip.point_depart, all_stops)
    end_coord = _resolve_coord(trip.point_arrivee, all_stops)

    start_point = None
    if start_coord:
        start_point = {"lat": start_coord[0], "lng": start_coord[1], "label": trip.point_depart}
    elif trip.point_depart:
        start_point = {"lat": None, "lng": None, "label": trip.point_depart}

    end_point = None
    if end_coord:
        end_point = {"lat": end_coord[0], "lng": end_coord[1], "label": trip.point_arrivee}
    elif trip.point_arrivee:
        end_point = {"lat": None, "lng": None, "label": trip.point_arrivee}

    # Parse arrets_circuit → try to resolve each to a coordinate
    parsed_stops = _parse_stops(trip.arrets_circuit)
    waypoints = []
    for stop_name in parsed_stops:
        coord = _resolve_coord(stop_name, all_stops)
        wp: dict[str, Any] = {
            "code": stop_name,
            "label": stop_name,
        }
        if coord:
            wp["lat"] = coord[0]
            wp["lng"] = coord[1]
        else:
            wp["lat"] = None
            wp["lng"] = None
        waypoints.append(wp)

    maps_url = _google_maps_url(
        trip.point_depart,
        trip.point_arrivee,
        [s["code"] for s in waypoints],
    )

    return TripDetailResponse(
        trip=_to_trip_item(trip),
        start_point=start_point,
        end_point=end_point,
        waypoints=waypoints,
        google_maps_url=maps_url,
    )
