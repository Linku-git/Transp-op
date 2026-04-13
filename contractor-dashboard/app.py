"""Contractor Dashboard -- Dash + Plotly micro-frontend for Transpop.

Runs independently on port 8050.  Authenticates via JWT against the
Transpop backend API.  All monetary values are in MAD (Moroccan Dirhams).
"""
from __future__ import annotations

import json
import logging
import os

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dotenv import load_dotenv

from services.auth import authenticate, validate_token

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Dash application
# ------------------------------------------------------------------ #

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
    ],
    suppress_callback_exceptions=True,
    title="Transpop - Portail Prestataire",
    update_title="Chargement...",
)

server = app.server  # Flask server for gunicorn

# ------------------------------------------------------------------ #
# Health check endpoint (Flask level)
# ------------------------------------------------------------------ #


@server.route("/health")
def health_check() -> tuple[str, int, dict[str, str]]:
    """Return health status as JSON."""
    return (
        json.dumps({"status": "healthy"}),
        200,
        {"Content-Type": "application/json"},
    )


# ------------------------------------------------------------------ #
# Sidebar component
# ------------------------------------------------------------------ #

NAV_ITEMS: list[dict[str, str]] = [
    {"label": "KPIs", "icon": "monitoring", "href": "/"},
    {"label": "SLA Compliance", "icon": "verified", "href": "/sla"},
    {"label": "Finances", "icon": "payments", "href": "/financial"},
    {"label": "Flotte", "icon": "directions_bus", "href": "/fleet"},
]


def _nav_link(item: dict[str, str]) -> dbc.NavLink:
    """Build a single sidebar nav link."""
    return dbc.NavLink(
        [
            html.Span(
                item["icon"],
                className="material-symbols-outlined me-2",
                style={"fontSize": "20px", "verticalAlign": "middle"},
            ),
            html.Span(item["label"]),
        ],
        href=item["href"],
        active="exact",
        className="rounded mb-1",
    )


sidebar = html.Div(
    [
        # Logo / brand
        html.Div(
            [
                html.Span(
                    "directions_bus",
                    className="material-symbols-outlined",
                    style={"fontSize": "32px", "color": "#0058be"},
                ),
                html.H5("Transpop", className="ms-2 mb-0 fw-bold"),
            ],
            className="d-flex align-items-center px-3 py-4",
        ),
        html.Hr(className="my-0"),
        # Navigation
        dbc.Nav(
            [_nav_link(item) for item in NAV_ITEMS],
            vertical=True,
            pills=True,
            className="px-2 py-3",
        ),
        # Footer
        html.Div(
            html.Small("v1.0.0 -- Portail Prestataire", className="text-muted"),
            className="px-3 py-3 mt-auto",
            style={"position": "absolute", "bottom": 0},
        ),
    ],
    className="bg-dark vh-100 position-fixed",
    style={"width": "250px", "overflowY": "auto"},
)

# ------------------------------------------------------------------ #
# Top navbar
# ------------------------------------------------------------------ #

top_navbar = dbc.Navbar(
    dbc.Container(
        [
            html.Div(id="navbar-contractor-name", className="text-light fw-bold"),
            dbc.Button(
                [
                    html.Span(
                        "logout",
                        className="material-symbols-outlined me-1",
                        style={"fontSize": "18px", "verticalAlign": "middle"},
                    ),
                    "Deconnexion",
                ],
                id="btn-logout",
                color="outline-light",
                size="sm",
            ),
        ],
        fluid=True,
        className="d-flex justify-content-between align-items-center",
    ),
    color="dark",
    dark=True,
    className="border-bottom border-secondary",
    style={"marginLeft": "250px"},
)

# ------------------------------------------------------------------ #
# Login layout
# ------------------------------------------------------------------ #

login_layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "lock",
                                    className="material-symbols-outlined",
                                    style={"fontSize": "48px", "color": "#0058be"},
                                ),
                            ],
                            className="text-center mb-3",
                        ),
                        html.H4(
                            "Portail Prestataire",
                            className="text-center mb-4",
                        ),
                        dbc.Input(
                            id="login-email",
                            type="email",
                            placeholder="Email",
                            className="mb-3",
                        ),
                        dbc.Input(
                            id="login-password",
                            type="password",
                            placeholder="Mot de passe",
                            className="mb-3",
                        ),
                        dbc.Button(
                            "Connexion",
                            id="btn-login",
                            color="primary",
                            className="w-100 mb-2",
                        ),
                        html.Div(id="login-error", className="text-danger text-center"),
                    ]
                ),
                className="shadow-lg border-0",
                style={"maxWidth": "400px"},
            ),
            width={"size": 4, "offset": 4},
            className="d-flex justify-content-center",
        ),
        className="vh-100 align-items-center",
    ),
    fluid=True,
)

# ------------------------------------------------------------------ #
# Main layout
# ------------------------------------------------------------------ #

app.layout = html.Div(
    [
        dcc.Store(id="session-token", storage_type="session"),
        dcc.Store(id="session-user", storage_type="session"),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ]
)

# ------------------------------------------------------------------ #
# Callbacks
# ------------------------------------------------------------------ #


@callback(
    Output("page-content", "children"),
    Input("session-token", "data"),
)
def render_page(token: str | None) -> html.Div:
    """Show login or main layout depending on auth state."""
    if not token:
        return login_layout

    return html.Div(
        [
            sidebar,
            top_navbar,
            html.Div(
                dash.page_container,
                style={
                    "marginLeft": "250px",
                    "padding": "24px",
                    "minHeight": "calc(100vh - 56px)",
                },
            ),
        ]
    )


@callback(
    Output("session-token", "data"),
    Output("session-user", "data"),
    Output("login-error", "children"),
    Input("btn-login", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def handle_login(
    n_clicks: int | None, email: str | None, password: str | None
) -> tuple[str | None, dict | None, str]:
    """Process login form submission."""
    if not n_clicks or not email or not password:
        return dash.no_update, dash.no_update, ""

    result = authenticate(email, password)
    if result:
        logger.info("User %s authenticated successfully", email)
        return result["token"], result["user"], ""

    return None, None, "Email ou mot de passe incorrect."


@callback(
    Output("session-token", "data", allow_duplicate=True),
    Output("session-user", "data", allow_duplicate=True),
    Input("btn-logout", "n_clicks"),
    prevent_initial_call=True,
)
def handle_logout(n_clicks: int | None) -> tuple[None, None]:
    """Clear session on logout."""
    if n_clicks:
        logger.info("User logged out")
    return None, None


@callback(
    Output("navbar-contractor-name", "children"),
    Input("session-user", "data"),
)
def update_navbar_name(user: dict | None) -> str:
    """Display contractor name in navbar."""
    if user:
        name: str = user.get("full_name", user.get("email", "Prestataire"))
        return name
    return "Prestataire"


# ------------------------------------------------------------------ #
# Entry point
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    port: int = int(os.getenv("PORT", "8050"))
    debug: bool = os.getenv("DASH_DEBUG", "true").lower() == "true"
    logger.info("Starting Contractor Dashboard on port %d (debug=%s)", port, debug)
    app.run(debug=debug, host="0.0.0.0", port=port)
