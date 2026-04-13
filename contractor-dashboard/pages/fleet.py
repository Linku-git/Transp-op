"""Fleet Status page -- Contractor Dashboard."""
from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from services.api_client import TranspopClient

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/fleet", name="Flotte", order=3)

# Status display configuration
STATUS_CONFIG: dict[str, dict[str, str]] = {
    "active": {"color": "#198754", "label": "Actif", "badge": "success"},
    "maintenance": {"color": "#ffc107", "label": "Maintenance", "badge": "warning"},
    "idle": {"color": "#6c757d", "label": "Inactif", "badge": "secondary"},
}

SEVERITY_BADGES: dict[str, str] = {
    "high": "danger",
    "medium": "warning",
    "low": "info",
}

# ------------------------------------------------------------------ #
# Layout
# ------------------------------------------------------------------ #

layout = html.Div(
    [
        # Header
        html.H4(
            [
                html.Span(
                    "directions_bus",
                    className="material-symbols-outlined me-2",
                    style={"verticalAlign": "middle"},
                ),
                "Etat de la Flotte",
            ],
            className="mb-4",
        ),
        # Map + Availability
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Position des Vehicules",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                dcc.Graph(
                                    id="fleet-map",
                                    config={"displayModeBar": False},
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=8,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Disponibilite par Type",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                dcc.Graph(
                                    id="fleet-availability-chart",
                                    config={"displayModeBar": False},
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=4,
                ),
            ],
            className="mb-4 g-3",
        ),
        # Vehicle table + Maintenance table
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Liste des Vehicules",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                html.Div(id="fleet-vehicle-table"),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=7,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Planning Maintenance",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                html.Div(id="fleet-maintenance-table"),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=5,
                ),
            ],
            className="g-3",
        ),
    ]
)

# ------------------------------------------------------------------ #
# Callbacks
# ------------------------------------------------------------------ #


@callback(
    Output("fleet-map", "figure"),
    Output("fleet-availability-chart", "figure"),
    Output("fleet-vehicle-table", "children"),
    Output("fleet-maintenance-table", "children"),
    Input("fleet-map", "id"),  # trigger on page load
)
def update_fleet(_: str) -> tuple[go.Figure, go.Figure, dbc.Table, dbc.Table]:
    """Load fleet data and render all components."""
    client = TranspopClient()
    data = client.get_fleet_status()

    vehicles = data["vehicles"]
    maintenance = data["maintenance_schedule"]
    availability = data["availability_by_type"]

    # ---- Scattermapbox ----
    lats: list[float] = [v["lat"] for v in vehicles]
    lngs: list[float] = [v["lng"] for v in vehicles]
    colors: list[str] = [
        STATUS_CONFIG.get(v["status"], STATUS_CONFIG["idle"])["color"]
        for v in vehicles
    ]
    labels: list[str] = [
        f"{v['plate']}<br>{v['type']}<br>Carburant: {v['fuel_pct']}%"
        for v in vehicles
    ]

    fleet_map = go.Figure()
    fleet_map.add_trace(
        go.Scattermapbox(
            lat=lats,
            lon=lngs,
            mode="markers",
            marker={"size": 14, "color": colors, "opacity": 0.9},
            text=labels,
            hoverinfo="text",
        )
    )
    fleet_map.update_layout(
        mapbox={
            "style": "carto-darkmatter",
            "center": {"lat": 33.57, "lon": -7.59},
            "zoom": 11,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        height=400,
        showlegend=False,
    )

    # ---- Availability doughnut ----
    types = list(availability.keys())
    avail_values = list(availability.values())
    doughnut_colors: list[str] = ["#0058be", "#0d6efd", "#6ea8fe"]

    avail_chart = go.Figure()
    avail_chart.add_trace(
        go.Pie(
            labels=types,
            values=avail_values,
            hole=0.55,
            marker={"colors": doughnut_colors[: len(types)]},
            textinfo="label+percent",
            textfont={"color": "#dee2e6"},
        )
    )
    avail_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=400,
        margin={"t": 20, "b": 20, "l": 20, "r": 20},
        showlegend=True,
        legend={"font": {"color": "#dee2e6"}},
    )

    # ---- Vehicle table ----
    vehicle_rows: list[html.Tr] = []
    for v in vehicles:
        cfg = STATUS_CONFIG.get(v["status"], STATUS_CONFIG["idle"])
        fuel_color: str = (
            "success" if v["fuel_pct"] >= 50 else "warning" if v["fuel_pct"] >= 25 else "danger"
        )
        vehicle_rows.append(
            html.Tr(
                [
                    html.Td(v["plate"], className="fw-bold"),
                    html.Td(v["type"]),
                    html.Td(
                        dbc.Badge(
                            cfg["label"],
                            color=cfg["badge"],
                            className="px-2 py-1",
                        )
                    ),
                    html.Td(
                        dbc.Progress(
                            value=v["fuel_pct"],
                            label=f"{v['fuel_pct']}%",
                            color=fuel_color,
                            style={"height": "20px"},
                        )
                    ),
                ]
            )
        )

    vehicle_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Immatriculation"),
                        html.Th("Type"),
                        html.Th("Statut"),
                        html.Th("Carburant"),
                    ]
                )
            ),
            html.Tbody(vehicle_rows),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
        className="mb-0",
    )

    # ---- Maintenance table ----
    maint_rows: list[html.Tr] = []
    for m in maintenance:
        severity_badge: str = SEVERITY_BADGES.get(m["severity"], "secondary")
        maint_rows.append(
            html.Tr(
                [
                    html.Td(m["vehicle"], className="fw-bold"),
                    html.Td(m["type"]),
                    html.Td(m["due_date"]),
                    html.Td(
                        dbc.Badge(
                            m["severity"].upper(),
                            color=severity_badge,
                            className="px-2 py-1",
                        )
                    ),
                ]
            )
        )

    maint_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Vehicule"),
                        html.Th("Type"),
                        html.Th("Echeance"),
                        html.Th("Severite"),
                    ]
                )
            ),
            html.Tbody(maint_rows),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
        className="mb-0",
    )

    return fleet_map, avail_chart, vehicle_table, maint_table
