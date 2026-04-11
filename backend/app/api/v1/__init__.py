from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.clusters import router as clusters_router
from app.api.v1.employees import router as employees_router
from app.api.v1.excel_import import router as excel_import_router
from app.api.v1.health import router as health_router
from app.api.v1.leaves import router as leaves_router
from app.api.v1.modal import employee_modal_router, modal_stats_router
from app.api.v1.roles import router as roles_router
from app.api.v1.sites import router as sites_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.users import router as users_router
from app.api.v1.routes import router as routes_router
from app.api.v1.vehicle_assignments import router as vehicle_assignments_router
from app.api.v1.optimization import router as optimization_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.scenarios import router as scenarios_router
from app.api.v1.settings import router as settings_router
from app.api.v1.constraints import router as constraints_router
from app.api.v1.weather import router as weather_router
from app.api.v1.exports import router as exports_router
from app.api.v1.financial import router as financial_router
from app.api.v1.kpis import router as kpis_router
from app.api.v1.km_consommation import router as km_consommation_router
from app.api.v1.point_arret import router as point_arret_router
from app.api.v1.configuration_transport import router as configuration_transport_router
from app.api.v1.configuration_plans import router as configuration_plans_router
from app.api.v1.horaire_travail import router as horaire_travail_router
from app.api.v1.transport_optimization import router as transport_optimization_router
from app.api.v1.mobile import router as mobile_router
from app.api.v1.rti_risk_stops import router as rti_risk_stops_router
from app.api.v1.rti import router as rti_router
from app.api.v1.rti_config import router as rti_config_router
from app.api.v1.kpis_rti import router as kpis_rti_router
from app.api.v1.security_questionnaire import router as security_questionnaire_router
from app.api.v1.security_scores import router as security_scores_router
from app.api.v1.security_risk_map import router as security_risk_map_router
from app.api.v1.kpis_security import router as kpis_security_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.content_analytics import router as content_analytics_router
from app.api.v1.content_feed import router as content_feed_router
from app.api.v1.content import router as content_router
from app.api.v1.surveys import router as surveys_router
from app.api.v1.training import router as training_router
from app.api.v1.valorization import router as valorization_router
from app.api.v1.sirh import router as sirh_router
from app.api.v1.operators import router as operators_router
from app.api.v1.operator_portal import router as operator_portal_router
from app.api.v1.financial_export import router as financial_export_router
from app.api.v1.payment import router as payment_router
from app.api.v1.gdpr import router as gdpr_router
from app.api.v1.sotreg_lignes import router as sotreg_lignes_router
from app.api.v1.sotreg_context import router as sotreg_context_router
from app.api.v1.sotreg_od import router as sotreg_od_router
from app.api.v1.sotreg_technologies import router as sotreg_technologies_router
from app.api.v1.sotreg_stops import router as sotreg_stops_router
from app.api.v1.sotreg_depot import router as sotreg_depot_router
from app.api.v1.sotreg_performance import router as sotreg_performance_router
from app.api.v1.sotreg_telemetry import router as sotreg_telemetry_router
from app.api.v1.sotreg_finance import router as sotreg_finance_router
from app.api.v1.sotreg_roadmap import router as sotreg_roadmap_router
from app.api.v1.sotreg_scoring import router as sotreg_scoring_router
from app.api.v1.sotreg_ml import router as sotreg_ml_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(roles_router, tags=["roles"])
api_router.include_router(tenants_router, tags=["tenants"])
api_router.include_router(sites_router, tags=["sites"])
api_router.include_router(employees_router, tags=["employees"])
api_router.include_router(leaves_router, tags=["leaves"])
api_router.include_router(employee_modal_router, tags=["modal"])
api_router.include_router(modal_stats_router, tags=["modal"])
api_router.include_router(excel_import_router, tags=["import"])
api_router.include_router(clusters_router, tags=["clusters"])
api_router.include_router(optimization_router, tags=["optimization"])
api_router.include_router(vehicles_router, tags=["vehicles"])
api_router.include_router(vehicle_assignments_router, tags=["vehicle-assignments"])
api_router.include_router(routes_router, tags=["routes"])
api_router.include_router(scenarios_router, tags=["scenarios"])
api_router.include_router(settings_router, tags=["settings"])
api_router.include_router(constraints_router, tags=["constraints"])
api_router.include_router(weather_router, tags=["weather"])
api_router.include_router(exports_router, tags=["exports"])
api_router.include_router(financial_router, tags=["financial"])
api_router.include_router(kpis_router, tags=["kpis"])
api_router.include_router(km_consommation_router, tags=["km-consommation"])
api_router.include_router(point_arret_router, tags=["points-arret"])
api_router.include_router(configuration_transport_router, tags=["configuration-transport"])
api_router.include_router(configuration_plans_router, tags=["configuration-plans"])
api_router.include_router(horaire_travail_router, tags=["horaires-travail"])
api_router.include_router(transport_optimization_router, tags=["transport-optimization"])
api_router.include_router(mobile_router, tags=["mobile"])
api_router.include_router(rti_risk_stops_router, tags=["rti"])
api_router.include_router(rti_router, tags=["rti"])
api_router.include_router(rti_config_router, tags=["rti"])
api_router.include_router(kpis_rti_router, tags=["kpis"])
api_router.include_router(security_questionnaire_router, tags=["security"])
api_router.include_router(security_scores_router, tags=["security"])
api_router.include_router(security_risk_map_router, tags=["security"])
api_router.include_router(kpis_security_router, tags=["kpis"])
api_router.include_router(emergency_router, tags=["security"])
api_router.include_router(content_analytics_router, tags=["content"])
api_router.include_router(content_feed_router, tags=["content"])
api_router.include_router(content_router, tags=["content"])
api_router.include_router(surveys_router, tags=["surveys"])
api_router.include_router(training_router, tags=["training"])
api_router.include_router(valorization_router, tags=["valorization"])
api_router.include_router(sirh_router, tags=["sirh"])
api_router.include_router(operators_router, tags=["operators"])
api_router.include_router(operator_portal_router, tags=["operator-portal"])
api_router.include_router(financial_export_router, tags=["financial"])
api_router.include_router(payment_router, tags=["payment"])
api_router.include_router(gdpr_router, tags=["rgpd"])
api_router.include_router(sotreg_lignes_router, tags=["sotreg"])
api_router.include_router(sotreg_context_router, tags=["sotreg"])
api_router.include_router(sotreg_od_router, tags=["sotreg"])
api_router.include_router(sotreg_technologies_router, tags=["sotreg"])
api_router.include_router(sotreg_stops_router, tags=["sotreg"])
api_router.include_router(sotreg_depot_router, tags=["sotreg"])
api_router.include_router(sotreg_performance_router, tags=["sotreg"])
api_router.include_router(sotreg_telemetry_router, tags=["sotreg"])
api_router.include_router(sotreg_finance_router, tags=["sotreg"])
api_router.include_router(sotreg_roadmap_router, tags=["sotreg"])
api_router.include_router(sotreg_scoring_router, tags=["sotreg"])
api_router.include_router(sotreg_ml_router, tags=["sotreg"])
