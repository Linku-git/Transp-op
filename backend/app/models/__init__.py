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
]
