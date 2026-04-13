"""Custom Rasa actions for the Transpop chatbot.

Each action queries the Transpop backend API via TranspopChatbotClient
and formats the response in French for the user.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.api_client import TranspopChatbotClient

logger = logging.getLogger(__name__)


class ActionQueryFleetStatus(Action):
    """Query fleet status from Transpop API and return summary."""

    def name(self) -> Text:
        return "action_query_fleet_status"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        client = TranspopChatbotClient()
        data = client.get_fleet_summary()

        if data:
            total = data.get("total", 0)
            active = data.get("active", 0)
            maintenance = data.get("maintenance", 0)
            inactive = data.get("inactive", 0)

            msg = (
                f"Flotte Transpop :\n"
                f"- Total : {total} vehicules\n"
                f"- Actifs : {active}\n"
                f"- En maintenance : {maintenance}\n"
                f"- Inactifs : {inactive}"
            )

            # Add electric/diesel breakdown if available
            electric = data.get("electric")
            diesel = data.get("diesel")
            if electric is not None or diesel is not None:
                msg += f"\n- Electriques : {electric or 0}"
                msg += f"\n- Diesel : {diesel or 0}"
        else:
            msg = (
                "Desole, je ne peux pas acceder aux donnees de la flotte "
                "pour le moment. Veuillez reessayer plus tard."
            )

        dispatcher.utter_message(text=msg)
        logger.info("Fleet status action completed")
        return []


class ActionQueryTripInfo(Action):
    """Query trip information for a specific ligne."""

    def name(self) -> Text:
        return "action_query_trip_info"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        ligne_id = tracker.get_slot("ligne_id")
        client = TranspopChatbotClient()

        if ligne_id:
            data = client.get_trip_info(ligne_id)
            if data:
                name = data.get("name", f"Ligne {ligne_id}")
                status = data.get("status", "inconnu")
                next_dep = data.get("next_departure", "non disponible")
                stops = data.get("stops", "N/A")
                duration = data.get("duration_min", "N/A")

                status_fr = {
                    "active": "active",
                    "inactive": "inactive",
                    "suspended": "suspendue",
                }.get(status, status)

                msg = (
                    f"Informations sur {name} :\n"
                    f"- Statut : {status_fr}\n"
                    f"- Prochain depart : {next_dep}\n"
                    f"- Nombre d'arrets : {stops}\n"
                    f"- Duree estimee : {duration} min"
                )
            else:
                msg = (
                    f"Desole, je ne trouve pas d'informations pour la ligne {ligne_id}. "
                    "Verifiez le numero de ligne et reessayez."
                )
        else:
            msg = (
                "Pour quelle ligne souhaitez-vous des informations ? "
                "Indiquez le numero de ligne (ex: 'ligne 5')."
            )

        dispatcher.utter_message(text=msg)
        logger.info("Trip info action completed for ligne_id=%s", ligne_id)
        return []


class ActionQueryKPI(Action):
    """Query KPI dashboard metrics."""

    def name(self) -> Text:
        return "action_query_kpi"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        kpi_type = tracker.get_slot("kpi_type")
        client = TranspopChatbotClient()
        data = client.get_kpi_dashboard()

        if data:
            if kpi_type:
                # Try to find specific KPI
                kpi_type_lower = kpi_type.lower()
                if "otp" in kpi_type_lower or "ponctualite" in kpi_type_lower:
                    value = data.get("otp", data.get("on_time_performance", "N/A"))
                    msg = f"Taux de ponctualite (OTP) : {value}%"
                elif "remplissage" in kpi_type_lower or "occupation" in kpi_type_lower:
                    value = data.get("fill_rate", data.get("avg_fill_rate", "N/A"))
                    msg = f"Taux de remplissage moyen : {value}%"
                elif "co2" in kpi_type_lower:
                    value = data.get("co2_saved_kg", data.get("co2_savings", "N/A"))
                    msg = f"CO2 economise : {value} kg"
                elif "headway" in kpi_type_lower:
                    value = data.get("avg_headway_min", data.get("headway", "N/A"))
                    msg = f"Intervalle moyen (headway) : {value} min"
                elif "retard" in kpi_type_lower or "delay" in kpi_type_lower:
                    value = data.get("avg_delay_min", data.get("average_delay", "N/A"))
                    msg = f"Retard moyen : {value} min"
                else:
                    msg = (
                        f"Je n'ai pas trouve le KPI '{kpi_type}'. "
                        "Les KPIs disponibles sont : OTP, remplissage, CO2, headway, retard."
                    )
            else:
                # Return full dashboard summary
                otp = data.get("otp", data.get("on_time_performance", "N/A"))
                fill = data.get("fill_rate", data.get("avg_fill_rate", "N/A"))
                co2 = data.get("co2_saved_kg", data.get("co2_savings", "N/A"))
                trips = data.get("total_trips", data.get("trips_count", "N/A"))
                delay = data.get("avg_delay_min", data.get("average_delay", "N/A"))

                msg = (
                    f"Indicateurs de performance :\n"
                    f"- Ponctualite (OTP) : {otp}%\n"
                    f"- Taux de remplissage : {fill}%\n"
                    f"- CO2 economise : {co2} kg\n"
                    f"- Trajets effectues : {trips}\n"
                    f"- Retard moyen : {delay} min"
                )
        else:
            msg = (
                "Desole, les indicateurs de performance ne sont pas disponibles "
                "pour le moment. Veuillez reessayer plus tard."
            )

        dispatcher.utter_message(text=msg)
        logger.info("KPI query action completed for kpi_type=%s", kpi_type)
        return []


class ActionQueryMaintenance(Action):
    """Query maintenance alerts from telemetry system."""

    def name(self) -> Text:
        return "action_query_maintenance"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        client = TranspopChatbotClient()
        data = client.get_maintenance_alerts()

        if data:
            total = data.get("total_alerts", data.get("total", 0))
            critical = data.get("critical", 0)
            warning = data.get("warning", 0)
            info_count = data.get("info", 0)

            msg = (
                f"Alertes maintenance :\n"
                f"- Total : {total} alertes\n"
                f"- Critiques : {critical}\n"
                f"- Avertissements : {warning}\n"
                f"- Informations : {info_count}"
            )

            # Add top alerts if available
            alerts = data.get("alerts", [])
            if alerts:
                msg += "\n\nDernieres alertes :"
                for alert in alerts[:3]:
                    vehicle = alert.get("vehicle", alert.get("vehicle_id", "?"))
                    alert_type = alert.get("type", alert.get("severity", "info"))
                    message = alert.get("message", alert.get("description", ""))
                    type_emoji = {"critical": "[CRITIQUE]", "warning": "[ATTENTION]"}.get(
                        alert_type, "[INFO]"
                    )
                    msg += f"\n  {type_emoji} {vehicle} : {message}"
        else:
            msg = (
                "Desole, les alertes de maintenance ne sont pas disponibles "
                "pour le moment. Veuillez reessayer plus tard."
            )

        dispatcher.utter_message(text=msg)
        logger.info("Maintenance query action completed")
        return []


class ActionQuerySchedule(Action):
    """Query driver schedule / upcoming trips."""

    def name(self) -> Text:
        return "action_query_schedule"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        date_slot = tracker.get_slot("date")
        driver_name = tracker.get_slot("driver_name")
        client = TranspopChatbotClient()
        data = client.get_driver_schedule(driver_id=None)

        if data:
            driver = data.get("driver", "Conducteur")
            shifts = data.get("shifts", data.get("data", []))

            if shifts:
                msg = f"Planning de {driver} :"
                for shift in shifts[:5]:
                    shift_date = shift.get("date", "")
                    start = shift.get("start", shift.get("start_time", ""))
                    end = shift.get("end", shift.get("end_time", ""))
                    ligne = shift.get("ligne", shift.get("ligne_name", ""))
                    msg += f"\n  - {shift_date} : {start} - {end} ({ligne})"

                if date_slot:
                    msg += f"\n\n(Filtre demande : {date_slot})"
            else:
                msg = "Aucun trajet programme pour le moment."
        else:
            msg = (
                "Desole, le planning n'est pas disponible pour le moment. "
                "Veuillez reessayer plus tard."
            )

        dispatcher.utter_message(text=msg)
        logger.info(
            "Schedule query action completed for date=%s, driver=%s",
            date_slot,
            driver_name,
        )
        return []
