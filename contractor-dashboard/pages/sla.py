"""SLA Compliance page -- Contractor Dashboard."""
from __future__ import annotations

import io
import logging

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from components.kpi_card import format_mad
from services.api_client import TranspopClient

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/sla", name="SLA Compliance", order=1)

# ------------------------------------------------------------------ #
# Layout
# ------------------------------------------------------------------ #

layout = html.Div(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    html.H4(
                        [
                            html.Span(
                                "verified",
                                className="material-symbols-outlined me-2",
                                style={"verticalAlign": "middle"},
                            ),
                            "Conformite SLA",
                        ],
                        className="mb-0",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        [
                            html.Span(
                                "download",
                                className="material-symbols-outlined me-1",
                                style={"fontSize": "18px", "verticalAlign": "middle"},
                            ),
                            "Exporter CSV",
                        ],
                        id="sla-export-btn",
                        color="primary",
                        size="sm",
                    ),
                    width="auto",
                    className="ms-auto",
                ),
            ],
            className="mb-4 align-items-center",
        ),
        # Download component
        dcc.Download(id="sla-download"),
        # Summary cards
        dbc.Row(id="sla-summary-row", className="mb-4 g-3"),
        # OTP line chart
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "OTP Journalier (30 jours)",
                                className="text-muted text-uppercase small fw-bold mb-3",
                            ),
                            dcc.Graph(id="sla-otp-chart", config={"displayModeBar": False}),
                        ]
                    ),
                    className="shadow-sm border-0",
                ),
            ),
            className="mb-4",
        ),
        # Trend + Penalty table side by side
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(
                                    "Analyse de Tendance",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                dcc.Graph(
                                    id="sla-trend-chart", config={"displayModeBar": False}
                                ),
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
                                    "Detail des Penalites",
                                    className="text-muted text-uppercase small fw-bold mb-3",
                                ),
                                html.Div(id="sla-penalty-table"),
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
    Output("sla-summary-row", "children"),
    Output("sla-otp-chart", "figure"),
    Output("sla-trend-chart", "figure"),
    Output("sla-penalty-table", "children"),
    Input("sla-export-btn", "id"),  # trigger on page load
)
def update_sla(_: str) -> tuple[list, go.Figure, go.Figure, dbc.Table]:
    """Load SLA data and render all components."""
    client = TranspopClient()
    data = client.get_sla_data(30)

    daily = data["daily_data"]
    target: float = data["target_otp"]
    days_below: int = sum(1 for d in daily if d["otp"] < target)

    # Summary cards
    summary = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small("OTP Moyen", className="text-muted text-uppercase fw-bold"),
                        html.H4(f"{data['avg_otp']:.1f}%", className="mb-0 fw-bold"),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small("Objectif OTP", className="text-muted text-uppercase fw-bold"),
                        html.H4(f"{target:.1f}%", className="mb-0 fw-bold text-info"),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(
                            "Penalites Totales",
                            className="text-muted text-uppercase fw-bold",
                        ),
                        html.H4(
                            format_mad(data["total_penalty_mad"]),
                            className="mb-0 fw-bold text-danger",
                        ),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(
                            "Jours < Objectif",
                            className="text-muted text-uppercase fw-bold",
                        ),
                        html.H4(
                            f"{days_below} / {len(daily)}",
                            className="mb-0 fw-bold text-warning",
                        ),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=3,
        ),
    ]

    # OTP line chart
    dates = [d["date"] for d in daily]
    otps = [d["otp"] for d in daily]

    otp_chart = go.Figure()
    otp_chart.add_trace(
        go.Scatter(
            x=dates,
            y=otps,
            mode="lines+markers",
            name="OTP",
            line={"color": "#0058be", "width": 2},
            marker={"size": 6},
        )
    )
    otp_chart.add_hline(
        y=target,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Objectif {target}%",
        annotation_position="top right",
        annotation_font_color="red",
    )
    otp_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=300,
        margin={"t": 30, "b": 40, "l": 50, "r": 20},
        xaxis={"title": "Date", "gridcolor": "rgba(255,255,255,0.1)"},
        yaxis={
            "title": "OTP (%)",
            "range": [80, 100],
            "gridcolor": "rgba(255,255,255,0.1)",
        },
        showlegend=False,
    )

    # Trend scatter with OLS trendline
    x_numeric = np.arange(len(otps), dtype=float)
    y_arr = np.array(otps, dtype=float)
    coeffs = np.polyfit(x_numeric, y_arr, 1)
    trend_y: list[float] = np.polyval(coeffs, x_numeric).tolist()

    trend_chart = go.Figure()
    trend_chart.add_trace(
        go.Scatter(
            x=dates,
            y=otps,
            mode="markers",
            name="OTP",
            marker={"color": "#0058be", "size": 8},
        )
    )
    trend_chart.add_trace(
        go.Scatter(
            x=dates,
            y=trend_y,
            mode="lines",
            name="Tendance",
            line={"color": "#ffaa00", "width": 2, "dash": "dot"},
        )
    )
    trend_direction: str = "hausse" if coeffs[0] > 0 else "baisse"
    trend_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=300,
        margin={"t": 30, "b": 40, "l": 50, "r": 20},
        xaxis={"gridcolor": "rgba(255,255,255,0.1)"},
        yaxis={"range": [80, 100], "gridcolor": "rgba(255,255,255,0.1)"},
        annotations=[
            {
                "text": f"Tendance: {trend_direction} ({coeffs[0]:+.3f}%/jour)",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 1.05,
                "showarrow": False,
                "font": {"color": "#dee2e6", "size": 12},
            }
        ],
    )

    # Penalty table (only rows with penalties)
    penalty_rows = [d for d in daily if d["penalty_mad"] > 0]
    table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Date"),
                        html.Th("OTP (%)"),
                        html.Th("Penalite (MAD)"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["date"]),
                            html.Td(
                                f"{row['otp']:.1f}%",
                                className="text-warning",
                            ),
                            html.Td(
                                format_mad(row["penalty_mad"]),
                                className="text-danger fw-bold",
                            ),
                        ]
                    )
                    for row in penalty_rows
                ]
            ),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
        className="mb-0",
        style={"maxHeight": "300px", "overflowY": "auto"},
    )

    return summary, otp_chart, trend_chart, table


@callback(
    Output("sla-download", "data"),
    Input("sla-export-btn", "n_clicks"),
    prevent_initial_call=True,
)
def export_sla_csv(n_clicks: int | None) -> dict | None:
    """Export SLA data as CSV."""
    if not n_clicks:
        return None

    client = TranspopClient()
    data = client.get_sla_data(30)
    df = pd.DataFrame(data["daily_data"])
    return dcc.send_data_frame(df.to_csv, "sla_report.csv", index=False)
