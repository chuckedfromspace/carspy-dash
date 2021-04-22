import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from utils import plot_cars, synthesize_cars


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


def synth_inputs(name, unit, id_addon, id_input, value,
                 tooltiptext):
    inputgroup = dbc.InputGroup(
        [
            dbc.InputGroupAddon(name, id=id_addon, addon_type="prepend"),
            dbc.Input(id=id_input, value=value, debounce=True),
            dbc.InputGroupAddon(unit, addon_type="append"),
            dbc.Tooltip(tooltiptext, target=id_addon, placement="bottom")
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
        className="mb-1"
    )
    return slider


# conditions-tab
def make_tab_conditions(P, T):
    tab_conditions = [
        input_slider("Gas pressure [Bar]", "P-input",
                     P, 0.5, 20, 0.5),
        input_slider("Gas temperature [K]", "T-input",
                     T, 300, 3000, 1),
    ]

    return tab_conditions


# models-tab
def make_tab_models(nu_start, nu_end, pump_ls, chi_rs, convol, doppler_effect,
                    pump_lw):
    range_slider = dbc.FormGroup(
        [
            dbc.InputGroupAddon("Spectral Range [1/cm]"),
            dcc.RangeSlider(id="spectral-range", min=2200, max=2360, step=2,
                            value=[nu_start, nu_end],
                            allowCross=False,
                            className="mt-1",
                            tooltip={"always_visible": False,
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
                     "pump_lw-input", pump_lw, 0.01, 5, 0.02),
        range_slider
    ]

    return tab_models


@app.callback(
    Output("synth-settings-card", "children"),
    Input("synth-settings", "active_tab"),
    State("memory-settings-conditions", "data"),
    State("memory-settings-models", "data"),
)
def tab_content(active_tab, data_1, data_2):
    if active_tab == "synth-settings-1":
        return make_tab_conditions(data_1["pressure"],  data_1["temperature"])
    else:
        return make_tab_models(data_2["nu_start"], data_2["nu_end"],
                               data_2["pump_ls"], data_2["chi_rs"],
                               data_2["convol"], data_2["doppler_effect"],
                               data_2["pump_lw"])


@app.callback(
    Output("memory-settings-conditions", "data"),
    [
        Input('P-input', 'value'),
        Input('T-input', 'value'),
        State("memory-settings-conditions", "data"),
    ]
)
def update_memory_conditions(P, T, data):
    data['pressure'] = P
    data['temperature'] = T
    return data


@app.callback(
    Output("memory-settings-models", "data"),
    [
        Input('pump_ls-select', 'value'),
        Input('chi_rs-select', 'value'),
        Input('convol-select', 'value'),
        Input('doppler-select', 'value'),
        Input('pump_lw-input', 'value'),
        Input('spectral-range', 'value'),
        State("memory-settings-models", "data"),
    ]
)
def update_memory_models(pump_ls, chi_rs, convol, doppler_effect, pump_lw,
                         spectral_range, data):
    data["nu_start"] = spectral_range[0]
    data["nu_end"] = spectral_range[1]
    data["pump_ls"] = pump_ls
    data["chi_rs"] = chi_rs
    data["convol"] = convol
    data["doppler_effect"] = doppler_effect
    data["pump_lw"] = pump_lw

    return data


@app.callback(
    Output("synth-signal", "figure"),
    [
        Input("memory-settings-conditions", "data"),
        Input("memory-settings-models", "data")
    ],
)
def update_test(data_1, data_2):
    if data_2["doppler_effect"] == "enable":
        data_2["doppler_effect"] = True
    else:
        data_2["doppler_effect"] = False
    nu, spect = synthesize_cars(**data_1, **data_2)
    return plot_cars(nu, spect)


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
        style={"height": "510px"},
        className="border-0"
    ),
    width=12,
    md=5,
    className="tab-col mb-2"
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
                    dbc.Spinner(
                        dcc.Graph(id="synth-signal", figure=plot_cars()),
                        color="primary"
                    ),
                ]
            ),
        ],
        style={"height": "510px"},
        className="border-0"
    ),
    width=12,
    md=7,
    className="tab-col mb-2"
)

tab_synth = dbc.Row(
    [
        card_setting,
        card_synth
    ],
    className="mb-1",
)
