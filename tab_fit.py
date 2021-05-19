import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from utils import plot_cars, DEFAULT_FIG
from tab_synthesize import synth_mode_select, synth_inputs


# slit function settings tab
def make_tab_slit(sigma, k, a_sigma, a_k, sigma_L_l, sigma_L_h):
    tab_slit = [
        synth_mode_select("Slit function", "slit-addon", "slit-select",
                          ["sGaussian", "sVoigt"],
                          "Choose the type of slit function",
                          "sGaussian"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        synth_inputs("sigma", "sigma", sigma),
                        synth_inputs("k", "k", k),
                        synth_inputs("sigma_L_l", "sigma_L_l", sigma_L_l),
                    ],
                    className="tab-col pl-3"
                ),
                dbc.Col(
                    [
                        synth_inputs("a_sigma", "a_sigma", a_sigma),
                        synth_inputs("a_k", "a-k", a_k),
                        synth_inputs("sigma_L_h", "sigma_L_h", sigma_L_h),
                    ],
                    className="tab-col pr-3"
                ),
            ],
            className="mt-2 mb-2"
        ),
    ]
    return tab_slit


# original signal tab
def make_tab_origin():
    tab_origin = [
        dbc.RadioItems(
            options=[
                {"label": "Linear", "value": "Linear"},
                {"label": "Log", "value": "Log"},
            ],
            value="Linear",
            inline=True,
            id="change-y-scale"
        ),
        dbc.Spinner(
            dcc.Graph(id="synth-signal", figure=DEFAULT_FIG,
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
    return tab_origin


# make the settings tabs always with settings stored in the memories
@app.callback(
    Output("fit-settings-card", "children"),
    [
        Input("fit-settings", "active_tab"),
        Input("memory-settings-slit", "data")
    ]
)
def fit_settings_tab_content(active_tab, data_2):
    if active_tab == "fit-settings-2":
        return make_tab_slit(**data_2)


# createa graph tabs
@app.callback(
    Output("fit-graph", "children"),
    Input("tab-fit-graph", "active_tab"),
)
def update_fit_spectrum(active_tab):
    if active_tab == "tab-fit-origin":
        return make_tab_origin()


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
                        dbc.Tab(label="Fit Signal",
                                tab_id="tab-fit-signal"),
                        dbc.Tab(label="Original Signal",
                                tab_id="tab-fit-origin"),
                    ],
                    id="tab-fit-graph",
                    card=True,
                    active_tab="tab-fit-origin"
                ),
                style={"background-color": "#e9ecef"}
            ),
            dbc.CardBody(id="fit-graph"),
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
