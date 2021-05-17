import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash
import dash_bootstrap_components as dbc

from app import app


# settings panels
card_setting = dbc.Col(
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Fit Parameters",
                                tab_id="fit-settings-1"),
                        dbc.Tab(label="Slit Function",
                                tab_id="fit-settings-2"),
                    ],
                    id="fit-settings",
                    card=True,
                    active_tab="fit-settings-1",
                ),
                style={"background-color": "#e9ecef"}
            ),
            dbc.CardBody(
                id="fit-settings-card"
            ),
        ],
        style={"height": "540px"},
        className="border-0"
    ),
    xs=12,
    md=5,
    className="tab-col mb-2",
)

# signal panel
card_fit = dbc.Col(
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label="CARS Signal", disabled=True,
                                active_label_style={
                                    "background-color": "#e9ecef",
                                    "border-width": "1px 0 1px 0px",
                                    "border-top-color": "#e9ecef",
                                    "border-bottom-color": "#d8d8d8",
                                }),
                    ],
                    card=True,
                ),
                style={"background-color": "#e9ecef"}
            ),
            dbc.CardBody(
                [
                    dbc.Spinner(
                        dcc.Graph(id="fit-signal",
                                  className="mt-2"),
                        color="primary"
                    ),
                    dbc.Button(
                        html.I(
                            title="Reset to default",
                            className="fas fa-undo-alt ml-0",
                            style={"font-size": "1.5em"},
                        ),
                        className="float-right p-0 shadow-none",
                        color="link",
                        size="sm",
                        id="reset-button-fit",
                        n_clicks=0,
                    )
                ]
            ),
        ],
        style={"height": "540px"},
        className="border-0"
    ),
    xs=12,
    md=7,
    className="tab-col mb-2"
)

# combine the two cards together
tab_fit = dbc.Row(
    [
        card_setting,
        card_fit
    ],
    className="mb-1",
)
