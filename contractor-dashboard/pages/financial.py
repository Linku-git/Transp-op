"""Financial Reconciliation page -- Contractor Dashboard."""
from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html
from dash.dash_table import DataTable

from components.kpi_card import format_mad
from services.api_client import TranspopClient

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/financial", name="Finances", order=2)

# ------------------------------------------------------------------ #
# Layout
# ------------------------------------------------------------------ #

layout = html.Div(
    [
        # Header
        html.H4(
            [
                html.Span(
                    "payments",
                    className="material-symbols-outlined me-2",
                    style={"verticalAlign": "middle"},
                ),
                "Rapprochement Financier",
            ],
            className="mb-4",
        ),
        # Summary cards
        dbc.Row(id="financial-summary-row", className="mb-4 g-3"),
        # Invoiced vs actual table
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "Facturation par Ligne",
                                className="text-muted text-uppercase small fw-bold mb-3",
                            ),
                            html.Div(id="financial-table-container"),
                        ]
                    ),
                    className="shadow-sm border-0",
                ),
            ),
            className="mb-4",
        ),
        # Monthly revenue chart
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6(
                                "Revenus Mensuels (MAD)",
                                className="text-muted text-uppercase small fw-bold mb-3",
                            ),
                            dcc.Graph(
                                id="financial-revenue-chart",
                                config={"displayModeBar": False},
                            ),
                        ]
                    ),
                    className="shadow-sm border-0",
                ),
            ),
        ),
    ]
)

# ------------------------------------------------------------------ #
# Callbacks
# ------------------------------------------------------------------ #


@callback(
    Output("financial-summary-row", "children"),
    Output("financial-table-container", "children"),
    Output("financial-revenue-chart", "figure"),
    Input("financial-summary-row", "id"),  # trigger on page load
)
def update_financial(_: str) -> tuple[list, DataTable, go.Figure]:
    """Load financial data and render all components."""
    client = TranspopClient()
    data = client.get_financial_data()

    lignes = data["lignes"]
    total_invoiced: float = data["total_invoiced_mad"]
    total_disputed: float = data["total_disputed_mad"]
    paid_count: int = sum(1 for lg in lignes if lg["status"] == "paid")
    payment_rate: float = (paid_count / len(lignes) * 100) if lignes else 0

    # Summary cards
    summary = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(
                            "Total Facture",
                            className="text-muted text-uppercase fw-bold",
                        ),
                        html.H4(
                            format_mad(total_invoiced),
                            className="mb-0 fw-bold",
                        ),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(
                            "En Litige",
                            className="text-muted text-uppercase fw-bold",
                        ),
                        html.H4(
                            format_mad(total_disputed),
                            className="mb-0 fw-bold text-danger",
                        ),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(
                            "Taux de Paiement",
                            className="text-muted text-uppercase fw-bold",
                        ),
                        html.H4(
                            f"{payment_rate:.0f}%",
                            className="mb-0 fw-bold text-success",
                        ),
                    ]
                ),
                className="shadow-sm border-0",
            ),
            md=4,
        ),
    ]

    # Prepare table data with discrepancy flag
    table_data: list[dict] = []
    for lg in lignes:
        has_discrepancy: bool = lg["invoiced_trips"] != lg["actual_trips"]
        table_data.append(
            {
                "ligne": lg["ligne"],
                "invoiced_trips": lg["invoiced_trips"],
                "actual_trips": lg["actual_trips"],
                "amount_mad": f"{lg['amount_mad']:,.2f}",
                "status": lg["status"].upper(),
                "discrepancy": "OUI" if has_discrepancy else "",
            }
        )

    # Status color mapping for conditional formatting
    status_colors: dict[str, str] = {
        "PAID": "#198754",      # green
        "PENDING": "#ffc107",   # amber
        "DISPUTED": "#dc3545",  # red
    }

    style_data_conditional: list[dict] = [
        {
            "if": {"filter_query": '{status} = "PAID"'},
            "backgroundColor": "rgba(25,135,84,0.15)",
            "color": "#198754",
        },
        {
            "if": {"filter_query": '{status} = "PENDING"'},
            "backgroundColor": "rgba(255,193,7,0.15)",
            "color": "#ffc107",
        },
        {
            "if": {"filter_query": '{status} = "DISPUTED"'},
            "backgroundColor": "rgba(220,53,69,0.15)",
            "color": "#dc3545",
        },
        {
            "if": {"filter_query": '{discrepancy} = "OUI"'},
            "fontWeight": "bold",
        },
    ]

    table = DataTable(
        id="financial-datatable",
        columns=[
            {"name": "Ligne", "id": "ligne"},
            {"name": "Trajets Factures", "id": "invoiced_trips", "type": "numeric"},
            {"name": "Trajets Reels", "id": "actual_trips", "type": "numeric"},
            {"name": "Montant (MAD)", "id": "amount_mad"},
            {"name": "Statut", "id": "status"},
            {"name": "Ecart", "id": "discrepancy"},
        ],
        data=table_data,
        style_data_conditional=style_data_conditional,
        style_header={
            "backgroundColor": "#343a40",
            "color": "#dee2e6",
            "fontWeight": "bold",
            "textTransform": "uppercase",
            "fontSize": "11px",
        },
        style_cell={
            "backgroundColor": "#212529",
            "color": "#dee2e6",
            "border": "1px solid #495057",
            "padding": "10px 12px",
            "textAlign": "left",
        },
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        sort_action="native",
        page_size=10,
    )

    # Monthly revenue bar chart
    monthly = data["monthly_revenue"]
    months = [m["month"] for m in monthly]
    revenues = [m["revenue_mad"] for m in monthly]

    revenue_chart = go.Figure()
    revenue_chart.add_trace(
        go.Bar(
            x=months,
            y=revenues,
            marker_color="#0058be",
            text=[f"{v:,.0f}" for v in revenues],
            textposition="outside",
            textfont={"color": "#dee2e6"},
        )
    )
    revenue_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dee2e6"},
        height=350,
        margin={"t": 30, "b": 40, "l": 60, "r": 20},
        xaxis={"title": "Mois", "gridcolor": "rgba(255,255,255,0.1)"},
        yaxis={
            "title": "Revenus (MAD)",
            "gridcolor": "rgba(255,255,255,0.1)",
            "tickformat": ",.0f",
        },
        showlegend=False,
    )

    return summary, table, revenue_chart
