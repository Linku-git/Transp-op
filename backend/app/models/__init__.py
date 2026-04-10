from app.models.auth import Permission, Role, RolePermission, Tenant, User
from app.models.base import BaseModel, TimestampMixin
from app.models.configuration_plan import ConfigurationPlan
from app.models.configuration_transport import ConfigurationTransport
from app.models.employee import Employee
from app.models.financial import (
    FinancialScenario,
    ROICalculation,
    TCOEntry,
    VehicleReference,
)
from app.models.generated_report import GeneratedReport
from app.models.km_consommation import KmConsommation
from app.models.kpi_snapshot import KPISnapshot
from app.models.leave import EmployeeLeave
from app.models.modal import EmployeeModal
from app.models.optimization import Cluster, Optimization, Route
from app.models.point_arret import PointArret
from app.models.site import Site
from app.models.scenario import Scenario
from app.models.settings import ConstraintParam, OptimizationSettings
from app.models.vehicle import Vehicle
from app.models.weather import WeatherForecast
from app.models.trip_booking import TripBooking
from app.models.device_registration import DeviceRegistration
from app.models.push_notification import PushNotification
from app.models.stop_risk_score import StopRiskScore
from app.models.vehicle_position import VehiclePosition as VehiclePositionModel
from app.models.rti_event import RTIEvent
from app.models.rti_config import RTIConfig
from app.models.security_questionnaire import SecurityQuestionnaire
from app.models.security_score import SecurityScore
from app.models.clustering_config import ClusteringConfig
from app.models.emergency_alert import EmergencyAlert
from app.models.content import Content
from app.models.content_delivery import ContentDelivery
from app.models.survey import Survey
from app.models.survey_response import SurveyResponse
from app.models.training_module import TrainingModule
from app.models.sirh_connection import SIRHConnection
from app.models.sync_log import SyncLog
from app.models.sync_conflict import SyncConflict
from app.models.operator import Operator
from app.models.sizing_plan_export import SizingPlanExport
from app.models.ligne import Ligne
from app.models.fleet_context import FleetContext
from app.models.od_matrix import ODMatrix
from app.models.irve_infrastructure import IRVEInfrastructure
from app.models.generated_stop import GeneratedStop
from app.models.depot_plan import DepotPlan
from app.models.avl_metric import AVLMetric
from app.models.departure_schedule import DepartureSchedule
from app.models.telemetry_reading import TelemetryReading
from app.models.maintenance_alert import MaintenanceAlert

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "Permission",
    "Role",
    "RolePermission",
    "Tenant",
    "User",
    "Site",
    "Employee",
    "EmployeeLeave",
    "EmployeeModal",
    "FinancialScenario",
    "GeneratedReport",
    "KmConsommation",
    "KPISnapshot",
    "PointArret",
    "ConfigurationPlan",
    "ConfigurationTransport",
    "TCOEntry",
    "ROICalculation",
    "VehicleReference",
    "Optimization",
    "Cluster",
    "Route",
    "Scenario",
    "ConstraintParam",
    "OptimizationSettings",
    "Vehicle",
    "WeatherForecast",
    "TripBooking",
    "DeviceRegistration",
    "PushNotification",
    "StopRiskScore",
    "VehiclePositionModel",
    "RTIEvent",
    "RTIConfig",
    "SecurityQuestionnaire",
    "SecurityScore",
    "ClusteringConfig",
    "EmergencyAlert",
    "Content",
    "ContentDelivery",
    "Survey",
    "SurveyResponse",
    "TrainingModule",
    "SIRHConnection",
    "SyncLog",
    "SyncConflict",
    "Operator",
    "SizingPlanExport",
    "Ligne",
    "FleetContext",
    "ODMatrix",
    "IRVEInfrastructure",
    "GeneratedStop",
    "DepotPlan",
    "AVLMetric",
    "DepartureSchedule",
    "TelemetryReading",
    "MaintenanceAlert",
]
