"""Reusable KPI card component for Dash."""
from __future__ import annotations

from dash import html
import dash_bootstrap_components as dbc


def format_mad(value: float) -> str:
    """Format value as MAD currency."""
    return f"{value:,.2f} MAD"


def kpi_card(
    title: str, value: str, delta_pct: float, icon: str = "chart_data"
) -> dbc.Card:
    """Create a KPI card with value and delta indicator.

    Parameters
    ----------
    title:
        Label shown above the value.
    value:
        Formatted value string (e.g. "1,247" or "94.2%").
    delta_pct:
        Percentage change vs previous period.
    icon:
        Material Symbols icon name.
    """
    delta_color: str = "success" if delta_pct >= 0 else "danger"
    delta_icon: str = "arrow_upward" if delta_pct >= 0 else "arrow_downward"

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(
                            icon,
                            className="material-symbols-outlined",
                            style={"fontSize": "24px"},
                        ),
                        html.Span(
                            title,
                            className="ms-2 text-muted small text-uppercase fw-bold",
                        ),
                    ],
                    className="d-flex align-items-center mb-2",
                ),
                html.H3(value, className="mb-1 fw-bold"),
                html.Small(
                    [
                        html.Span(
                            delta_icon,
                            className=f"material-symbols-outlined text-{delta_color}",
                            style={"fontSize": "14px", "verticalAlign": "middle"},
                        ),
                        html.Span(
                            f" {abs(delta_pct):.1f}%",
                            className=f"text-{delta_color} fw-bold",
                        ),
                        html.Span(
                            " vs periode precedente", className="text-muted ms-1"
                        ),
                    ]
                ),
            ]
        ),
        className="shadow-sm border-0",
    )
