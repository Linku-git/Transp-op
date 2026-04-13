"""KPI Overview page -- Contractor Dashboard."""
from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from components.kpi_card import kpi_card
from services.api_client import TranspopClient

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/", name="KPIs", order=0)

# ------------------------------------------------------------------ #
# Layout
# ------------------------------------------------------------------ #

layout = html.Div(
    [
        # Header row
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        [
                            html.Span(
                                "monitoring",
                                className="material-symbols-outlined me-2",
                                style={"verticalAlign": "middle"},
                            ),
                            "Tableau de Bord KPIs",
                        ],
                        className="mb-0",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Select(
                        id="kpi-period-select",
                        options=[
                            {"label": "Aujourd'hui", "value": "today"},
                            {"label": "Semaine", "value": "week"},
                            {"label": "Mois", "value": "month"},
                            {"label": "Trimestre", "value": "quarter"},
                        ],
                        value="month",
                        className="w-auto",
                    ),
                    width="auto",
                    className="ms-auto",
                ),
            ],
            className="mb-4 align-items-center",
        ),
        # KPI cards row
        dbc.Row(id="kpi-cards-row", className="mb-4 g-3"),
        # Charts row
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "OTP & Utilisation",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                dcc.Graph(id="kpi-gauges", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Tendance Trajets (30j)",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                dcc.Graph(id="kpi-sparkline", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    md=6,
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
    Output("kpi-cards-row", "children"),
    Output("kpi-gauges", "figure"),
    Output("kpi-sparkline", "figure"),
    Input("kpi-period-select", "value"),
)
def update_kpis(period: str) -> tuple[list, go.Figure, go.Figure]:
    """Fetch KPIs and update cards + charts."""
    client = TranspopClient()
    data = client.get_kpis(period)

    # Build KPI cards
    cards = [
        dbc.Col(
            kpi_card(
                "Trajets Effectues",
                f"{data['trips_completed']['value']:,}",
                data["trips_completed"]["delta_pct"],
                icon="route",
            ),
            md=3,
        ),
        dbc.Col(
            kpi_card(
                "Ponctualite (OTP)",
                f"{data['on_time_pct']['value']:.1f}%",
                data["on_time_pct"]["delta_pct"],
                icon="schedule",
            ),
            md=3,
        ),
        dbc.Col(
            kpi_card(
                "Satisfaction",
                f"{data['satisfaction']['value']:.1f}/5",
                data["satisfaction"]["delta_pct"],
                icon="sentiment_satisfied",
            ),
            md=3,
        ),
        dbc.Col(
            kpi_card(
                "Utilisation Flotte",
                f"{data['utilization']['value']:.1f}%",
                data["utilization"]["delta_pct"],
                icon="directions_bus",
            ),
            md=3,
        ),
    ]

    # Gauge charts
    gauges = go.Figure()
    gauges.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=data["on_time_pct"]["value"],
            delta={"reference": data["on_time_pct"]["previous"], "suffix": "%"},
            title={"text": "OTP (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0058be"},
                "steps": [
                    {"range": [0, 85], "color": "#ff4444"},
                    {"range": [85, 95], "color": "#ffaa00"},
                    {"range": [95, 100], "color": "#44bb44"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": 95,
                },
            },
            domain={"x": [0, 0.45], "y": [0, 1]},
        )
    )
    gauges.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=data["utilization"]["value"],
            delta={"reference": data["utilization"]["previous"], "suffix": "%"},
            title={"text": "Utilisation (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0058be"},
                "steps": [
                    {"range": [0, 60], "color": "#ff4444"},
                    {"range": [60, 80], "color": "#ffaa00"},
                    {"range": [80, 100], "color": "#44bb44"},
                ],
            },
            domain={"x": [0.55, 1], "y": [0, 1]},
        )
    )
    gauges.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=280,
        margin={"t": 40, "b": 20, "l": 30, "r": 30},
    )

    # Sparkline -- daily trip trend (simulated 30 days)
    import numpy as np

    rng = np.random.RandomState(42)
    days_range = list(range(1, 31))
    daily_trips: list[float] = (35 + rng.normal(0, 5, 30)).clip(20, 55).tolist()

    sparkline = go.Figure()
    sparkline.add_trace(
        go.Scatter(
            x=days_range,
            y=daily_trips,
            mode="lines+markers",
            line={"color": "#0058be", "width": 2},
            marker={"size": 4},
            fill="tozeroy",
            fillcolor="rgba(0,88,190,0.15)",
            name="Trajets/jour",
        )
    )
    sparkline.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=280,
        margin={"t": 10, "b": 30, "l": 40, "r": 10},
        xaxis={"title": "Jour du mois", "gridcolor": "rgba(255,255,255,0.1)"},
        yaxis={"title": "Trajets", "gridcolor": "rgba(255,255,255,0.1)"},
        showlegend=False,
    )

    return cards, gauges, sparkline
