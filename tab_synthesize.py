import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash
import dash_bootstrap_components as dbc

from app import app
from utils import (DEFAULT_SETTINGS_CONDITIONS, plot_cars, synthesize_cars,
                   DEFAULT_SETTINGS_MODELS)


def synth_mode_select(name, id_addon, id_select, options, tooltiptext,
                      value):
    inputgroup = dbc.InputGroup(
        [
            dbc.InputGroupAddon(name, id=id_addon,
                                addon_type="prepend"),
            dbc.Select(
                options=[
                    {'label': i, 'value': i} for i in options
                ],
                value=value,
                id=id_select,
            ),
            dbc.Tooltip(tooltiptext, target=id_addon, placement="bottom")
        ],
        className="mb-1"

    )
    return inputgroup


def synth_inputs(name, id_input, value):
    inputgroup = dbc.InputGroup(
        [
            dbc.InputGroupAddon(name, addon_type="prepend",
                                className="col-6 px-0"),
            dbc.Input(id=id_input, value=float(value), debounce=True,
                      className="col-6"),
            # dbc.InputGroupAddon("%", addon_type="append"),
        ],
        className="mb-1"
    )
    return inputgroup


def input_slider(name, input_id, value, value_min, value_max, step):
    slider = dbc.FormGroup(
        [
            dbc.InputGroupAddon(name, addon_type="prepend"),
            dcc.Slider(id=input_id, min=value_min, max=value_max, value=value,
                       step=step,
                       tooltip={"always_visible": True,
                                "placement": "bottom"},
                       className="mt-1"
                       ),
        ],
        className="mb-2"
    )
    return slider


# conditions-tab
def make_tab_conditions(P, T, x_N2, x_Ar, x_H2, x_O2,
                        x_CO2, x_CO, x_H2O, x_CH4):
    tab_conditions = [
        input_slider("Gas pressure [Bar]", "P-input",
                     P, 0.5, 20, 0.5),
        input_slider("Gas temperature [K]", "T-input",
                     T, 300, 3000, 1),
        dbc.InputGroupAddon("Gas composition", addon_type="prepend",
                            className="mt-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        synth_inputs("N2", "x-N2", x_N2),
                        synth_inputs("Ar", "x-Ar", x_Ar),
                        synth_inputs("H2", "x-H2", x_H2),
                        synth_inputs("O2", "x-O2", x_O2),
                    ],
                    className="tab-col pl-3"
                ),
                dbc.Col(
                    [
                        synth_inputs("CO2", "x-CO2", x_CO2),
                        synth_inputs("CO", "x-CO", x_CO),
                        synth_inputs("H2O", "x-H2O", x_H2O),
                        synth_inputs("CH4", "x-CH4", x_CH4),
                    ],
                    className="tab-col pr-3"
                ),
            ],
            className="mt-2 mb-2"
        ),
        synth_mode_select("Nonresonant BG", "chi_nr-addon", "chi_nr-select",
                          ["SET 3"],
                          "Choose the set of non-resonant background",
                          "SET 3")
    ]

    return tab_conditions


# models-tab
def make_tab_models(nu_start, nu_end, pump_ls, chi_rs, convol, doppler_effect,
                    pump_lw, num_sample):
    range_slider = dbc.FormGroup(
        [
            dbc.InputGroupAddon("Spectral Range [1/cm]"),
            dcc.RangeSlider(id="spectral-range", min=2200, max=2400, step=2,
                            value=[nu_start, nu_end],
                            allowCross=False,
                            className="mt-1",
                            tooltip={"always_visible": True,
                                     "placement": "bottom"}),
        ]
    )

    tab_models = [
        synth_mode_select("species", "species-addon",
                          "species-select",
                          ["N2"],
                          "Choose a species", "N2"),
        synth_mode_select("pump_ls", "pump_ls-addon",
                          "pump_ls-select",
                          ["Gaussian", "Lorentzian"],
                          "Choose a pump laser lineshape", pump_ls),
        synth_mode_select("chi_rs", "chi_rs-addon",
                          "chi_rs-select",
                          ["G-matrix", "isolated"],
                          "Choose a CARS model", chi_rs),
        synth_mode_select("convol", "convol-addon",
                          "convol-select",
                          ["Kataoka", "Yuratich"],
                          "Choose a convolution method", convol),
        synth_mode_select("doppler_effect", "doppler-addon",
                          "doppler-select",
                          ["enable", "disable"],
                          "Enable to consider Doppler broadening",
                          doppler_effect),
        input_slider("Pump laser linewdith [1/cm]",
                     "pump_lw-input", pump_lw, 0.02, 5, 0.02),
        input_slider("Number of sampling points",
                     "num_sample-input", num_sample, 8000, 30000, 2000),
        range_slider
    ]

    return tab_models


# make the settings tabs always with settings stored in the memories
@app.callback(
    Output("synth-settings-card", "children"),
    Input("synth-settings", "active_tab"),
    State("memory-settings-conditions", "data"),
    State("memory-settings-models", "data"),
)
def tab_content(active_tab, data_1, data_2):
    if active_tab == "synth-settings-1":
        return make_tab_conditions(data_1["pressure"],  data_1["temperature"],
                                   data_1["comp"]["N2"], data_1["comp"]["Ar"],
                                   data_1["comp"]["H2"], data_1["comp"]["O2"],
                                   data_1["comp"]["CO2"], data_1["comp"]["CO"],
                                   data_1["comp"]["H2O"], data_1["comp"]["CH4"]
                                   )
    else:
        return make_tab_models(data_2["nu_start"], data_2["nu_end"],
                               data_2["pump_ls"], data_2["chi_rs"],
                               data_2["convol"], data_2["doppler_effect"],
                               data_2["pump_lw"], data_2["num_sample"])


# reset the reset button n_clicks to 0 when switching between settings tabs
@app.callback(
    Output("reset-button", "n_clicks"),
    Input("synth-settings", "active_tab"),
)
def re_zero(active_tab):
    if active_tab:
        return 0


# store input conditions into the memory
@app.callback(
    Output("memory-settings-conditions", "data"),
    [
        Input('P-input', 'value'),
        Input('T-input', 'value'),
        Input('x-N2', 'value'),
        Input('x-Ar', 'value'),
        Input('x-H2', 'value'),
        Input('x-O2', 'value'),
        Input('x-CO2', 'value'),
        Input('x-CO', 'value'),
        Input('x-H2O', 'value'),
        Input('x-CH4', 'value'),
    ],
    State("memory-settings-conditions", "data"),
)
def update_memory_conditions(P, T, x_N2, x_Ar, x_H2, x_O2, x_CO2, x_CO, x_H2O,
                             x_CH4, data):
    data['pressure'] = P
    data['temperature'] = T
    data['comp']["N2"] = float(x_N2)
    data['comp']["Ar"] = float(x_Ar)
    data['comp']["H2"] = float(x_H2)
    data['comp']["O2"] = float(x_O2)
    data['comp']["CO2"] = float(x_CO2)
    data['comp']["CO"] = float(x_CO)
    data['comp']["H2O"] = float(x_H2O)
    data['comp']["CH4"] = float(x_CH4)
    return data


# reset the conditions tab when clicking the reset button
@app.callback(
    [
        Output('P-input', 'value'),
        Output('T-input', 'value'),
        Output('x-N2', 'value'),
        Output('x-Ar', 'value'),
        Output('x-H2', 'value'),
        Output('x-O2', 'value'),
        Output('x-CO2', 'value'),
        Output('x-CO', 'value'),
        Output('x-H2O', 'value'),
        Output('x-CH4', 'value'),
    ],
    Input('reset-button', 'n_clicks'),
    State("memory-settings-conditions", "data"),  # maybe not necessary
)
def reset_conditions(n, data):
    if n > 0:
        data = DEFAULT_SETTINGS_CONDITIONS
    _settings = [data["pressure"], data["temperature"], data['comp']["N2"],
                 data['comp']["Ar"], data['comp']["H2"], data['comp']["O2"],
                 data['comp']["CO2"], data['comp']["CO"], data['comp']["H2O"],
                 data['comp']["CH4"]]
    return _settings


# store models settings in the memory
@app.callback(
    Output("memory-settings-models", "data"),
    [
        Input('pump_ls-select', 'value'),
        Input('chi_rs-select', 'value'),
        Input('convol-select', 'value'),
        Input('doppler-select', 'value'),
        Input('pump_lw-input', 'value'),
        Input('spectral-range', 'value'),
        Input('num_sample-input', 'value'),
        State("memory-settings-models", "data"),
    ]
)
def update_memory_models(pump_ls, chi_rs, convol, doppler_effect, pump_lw,
                         spectral_range, num_sample, data):
    data["nu_start"] = spectral_range[0]
    data["nu_end"] = spectral_range[1]
    data["pump_ls"] = pump_ls
    data["chi_rs"] = chi_rs
    data["convol"] = convol
    data["doppler_effect"] = doppler_effect
    data["pump_lw"] = pump_lw
    data["num_sample"] = num_sample

    return data


# reset models settings when clicking the reset button
@app.callback(
    [
        Output('pump_ls-select', 'value'),
        Output('chi_rs-select', 'value'),
        Output('convol-select', 'value'),
        Output('doppler-select', 'value'),
        Output('pump_lw-input', 'value'),
        Output('spectral-range', 'value'),
        Output('num_sample-input', 'value'),
    ],
    Input('reset-button', 'n_clicks'),
    State("memory-settings-models", "data"),
)
def reset_models(n, data):
    if n > 0:
        data = DEFAULT_SETTINGS_MODELS
    _settings = [data["pump_ls"], data["chi_rs"], data["convol"],
                 data["doppler_effect"], data["pump_lw"],
                 [data["nu_start"], data["nu_end"]],
                 data["num_sample"]]
    return _settings


# plot spectrum and save spectrum data in memory
@app.callback(
    [
        Output("memory-synth-spectrum", "data"),
        Output("synth-signal", "figure"),
    ],
    [
        Input("memory-settings-conditions", "data"),
        Input("memory-settings-models", "data"),
        Input("change-y-scale", "value")
    ],
    State("memory-synth-spectrum", "data")
)
def update_synth_spectrum(data_1, data_2, y_scale, spect_memo):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == "change-y-scale":
        nu, spect = spect_memo
    else:
        if data_2["doppler_effect"] == "enable":
            data_2["doppler_effect"] = True
        else:
            data_2["doppler_effect"] = False
        nu, spect = synthesize_cars(**data_1, **data_2)
    figure = plot_cars(nu, spect, y_scale)
    return [nu, spect], figure


# setting panels
card_setting = dbc.Col(
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Conditions", tab_id="synth-settings-1"),
                        dbc.Tab(label="Models", tab_id="synth-settings-2"),
                    ],
                    id="synth-settings",
                    card=True,
                    active_tab="synth-settings-1",
                ),
                style={"background-color": "#e9ecef"}
            ),
            dbc.CardBody(
                id="synth-settings-card"
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
card_synth = dbc.Col(
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
                        dcc.Graph(id="synth-signal", figure=plot_cars(),
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
                        id="reset-button",
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
tab_synth = dbc.Row(
    [
        card_setting,
        card_synth
    ],
    className="mb-1",
)
