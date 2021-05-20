import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from utils import DEFAULT_SETTINGS_SLIT, plot_cars, plot_placeholder, plot_slit
from tab_synthesize import synth_mode_select, synth_inputs, input_slider


# slit function settings tab
def make_tab_slit(sigma, k, a_sigma, a_k, sigma_L_l, sigma_L_h, slit):
    tab_slit = [
        synth_mode_select("Slit function", "slit-addon", "slit-select",
                          ["sGaussian", "sVoigt"],
                          "Choose the type of slit function",
                          slit),
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
                        synth_inputs("a_k", "a_k", a_k),
                        synth_inputs("sigma_L_h", "sigma_L_h", sigma_L_h),
                    ],
                    className="tab-col pr-3"
                ),
            ],
            className="mt-2 mb-2"
        ),
        dbc.Spinner(
            dcc.Graph(
                id="graph-slit-function",
                figure=plot_placeholder(280)
            ),
            color="primary"
        )

    ]
    return tab_slit


# fit settings tab
def make_tab_fit(nu_start, nu_end, sample_length):
    tab_fit = [
        input_slider("Sample length",
                     "sample_length-input", sample_length, 60, 240, 20)
    ]
    return tab_fit


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
            dcc.Graph(id="synth-signal", figure=plot_placeholder(400),
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


# disable input based on slit function
@app.callback(
    [
        Output("sigma_L_l", "disabled"),
        Output("sigma_L_h", "disabled"),
    ],
    Input("slit-select", "value")
)
def disable_slit_input(value):
    if value == "sGaussian":
        return True, True
    else:
        return False, False


# plot slit graph
@app.callback(
    Output("graph-slit-function", "figure"),
    [
        Input("memory-settings-slit", "data"),
        Input("memory-synth-spectrum", "data"),
    ],
)
def update_slit_func(parameters, spect_memo):
    nu, _ = spect_memo
    return plot_slit(nu, parameters)


# update slit settings
@app.callback(
    Output("memory-settings-slit", "data"),
    [
        Input('sigma', 'value'),
        Input('a_sigma', 'value'),
        Input('k', 'value'),
        Input('a_k', 'value'),
        Input('sigma_L_l', 'value'),
        Input('sigma_L_h', 'value'),
        Input('slit-select', 'value')
    ],
    State("memory-settings-slit", "data"),
)
def update_memory_slit(sigma, a_sigma, k, a_k, sigma_L_l, sigma_L_h,
                       slit_shape, data):
    data["sigma"] = float(sigma)
    data["a_sigma"] = float(a_sigma)
    data["k"] = float(k)
    data["a_k"] = float(a_k)
    data["sigma_L_l"] = float(sigma_L_l)
    data["sigma_L_h"] = float(sigma_L_h)
    data["slit"] = slit_shape
    return data


# update slit settings
@app.callback(
    [
        Output('sigma', 'value'),
        Output('a_sigma', 'value'),
        Output('k', 'value'),
        Output('a_k', 'value'),
        Output('sigma_L_l', 'value'),
        Output('sigma_L_h', 'value'),
        Output('slit-select', 'value')
    ],
    Input('reset-button-fit', 'n_clicks'),
    State("memory-settings-slit", "data"),
)
def reset_slit(n, data):
    if n > 0:
        data = DEFAULT_SETTINGS_SLIT
    _settings = [data["sigma"], data["a_sigma"], data["k"], data["a_k"],
                 data["sigma_L_l"], data["sigma_L_h"], data["slit"]]
    return _settings


# reset the reset button n_clicks to 0 when switching between settings tabs
@app.callback(
    Output("reset-button-fit", "n_clicks"),
    Input("fit-settings", "active_tab"),
)
def re_zero_fit(active_tab):
    if active_tab:
        return 0


# make the settings tabs always with settings stored in the memories
@app.callback(
    Output("fit-settings-card", "children"),
    Input("fit-settings", "active_tab"),
    State("memory-settings-models", "data"),
    State("memory-settings-slit", "data")
)
def fit_settings_tab_content(active_tab, data_1, data_2):
    if active_tab == "fit-settings-1":
        return make_tab_fit(data_1["nu_start"]-5, data_1["nu_end"]-5, 120)
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
                    active_tab="fit-settings-2",
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
