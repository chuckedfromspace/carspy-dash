from pathlib import Path
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from carspy import CarsSpectrum

ICONS = 'https://use.fontawesome.com/releases/v5.15.3/css/all.css'
CUSTOM_CSS = "assets/custom.css"
app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.COSMO, ICONS])
server = app.server
app.title = 'CARSpy'
FLUID_STATE = True

'''
################################## Plots ######################################
'''
INIT_COMP = {'N2': 0.79,
             'Ar': 0.0,
             'CO2': 0,
             'CO': 0,
             'H2': 0,
             'O2': 0.21,
             'H2O': 0,
             'CH4': 0}

DEFAULT_SETTINGS = {
    "pressure": 1,
    "temperature": 1750,
    "pump_lw": 1.01,
    "nu_start": 2250,
    "nu_end": 2350,
    "pump_ls": "Gaussian",
    "chi_rs": "isolated",
    "convol": "Y",
    "doppler_effect": False
}


def synthesize_cars(pressure=1, temperature=1750, pump_lw=1.01,
                    nu_start=2250, nu_end=2350,
                    pump_ls='Gaussian', chi_rs='isolated',
                    convol='Y', doppler_effect=False):
    synth_mode = {'pump_ls': pump_ls,
                  'chi_rs': chi_rs,
                  'convol': convol,
                  'doppler_effect': doppler_effect,
                  'chem_eq': False}

    nu = np.linspace(nu_start, nu_end, num=10000)
    cars = CarsSpectrum(pressure=pressure, init_comp=INIT_COMP,
                        chi_set="SET 1")
    _, spect = cars.signal_as(temperature=temperature,
                              nu_s=nu,
                              synth_mode=synth_mode,
                              pump_lw=pump_lw)

    return nu, spect


def plot_cars(nu=None, spect=None):
    if nu is None and spect is None:
        nu, spect = synthesize_cars()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=nu, y=spect/spect.max(),
        mode='lines',
        name="CARS Signal",
    ))

    fig.update_traces(hoverinfo='skip', selector=dict(type='scatter'))
    fig.update_layout(height=400,
                      margin={'l': 20, 'b': 10, 'r': 10, 't': 10},
                      xaxis_title="Wavenumber [1/cm]",
                      yaxis_title="Signal [-]")

    return fig


'''
############################ General functions ################################
'''


def popup_modal(card_name, src=None, description="",
                modal_id="modal", close_id="close"):
    modal = dbc.Modal(
        [
            dbc.ModalHeader(card_name),
            dbc.ModalBody(
                [
                    html.Img(src=src, className="w-100"),
                    html.P(description)
                ]
                ),
            dbc.ModalFooter(
                dbc.Button("Close", id=close_id,
                           className="ml-auto")
            ),
        ],
        id=modal_id,
        size="lg",
        centered=True,
        backdrop="static"
    )
    return modal


def popup_menu(name, id, src, modal_id, close_id, description=""):
    menu_item = dbc.DropdownMenuItem(
        [
            name,
            popup_modal(name, src=src, modal_id=modal_id, close_id=close_id,
                        description=description)
        ],
        id=id,
    )
    return menu_item


def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


for _modal, _button, _close in zip(
        ["struc-modal", "models-modal", "vs1-modal", "vs2-modal",
         "info-modal"],
        ["struc-pop", "models-pop", "vs1-pop", "vs2-pop", "info-pop"],
        ["struc-close", "models-close", "vs1-close", "vs2-close",
         "info-close"]):
    app.callback(
        Output(_modal, "is_open"),
        [Input(_button, "n_clicks"), Input(_close, "n_clicks")],
        [State(_modal, "is_open")],
    )(toggle_modal)


def synth_mode_select(name, id_addon, id_select, options, tooltiptext,
                      default_option=1):
    inputgroup = dbc.InputGroup(
        [
            dbc.InputGroupAddon(name, id=id_addon,
                                addon_type="prepend"),
            dbc.Select(
                options=[
                    {'label': i, 'value': i} for i in options
                ],
                value=options[default_option],
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


'''
################################# Navbar ######################################
'''
# load the markdown file
with open(Path(__file__).parent / "intro.md", "r") as f:
    intro_md = f.read()

# features
IMG_STRUCT = ("https://raw.githubusercontent.com/chuckedfromspace/carspy/"
              + "main/assets/carspy_struct.png")
IMG_MODEL = ("https://raw.githubusercontent.com/chuckedfromspace/carspy/"
             + "main/assets/cars_model.png")
IMG_COMPARE1 = ("https://raw.githubusercontent.com/chuckedfromspace/carspy/"
                + "main/assets/vs_CARSFT_01.jpeg")
IMG_COMPARE2 = ("https://raw.githubusercontent.com/chuckedfromspace/carspy/"
                + "main/assets/vs_CARSFT_02.jpeg")
CAP_1 = ("Synthesized CARS spectra in N2 at 1 atm, 2400 K, "
         + "with a pump linewidth of 0.5 cm-1, "
         + "using Voigt lineshape and cross-coherence convolution.")
CAP_2 = ("Synthesized CARS spectra in N2 at 10 atm, 2400 K, "
         + "with a pump linewidth of 0.5 cm-1, using modified exponential "
         + "gap law (MEG) and cross-coherence convolution")
feature_menu = dbc.DropdownMenu(
    [
        popup_menu("CARSpy Structure",
                   id="struc-pop",
                   src=IMG_STRUCT,
                   modal_id="struc-modal",
                   close_id="struc-close"),
        popup_menu("CARS Models",
                   id="models-pop",
                   src=IMG_MODEL,
                   modal_id="models-modal",
                   close_id="models-close"),
        popup_menu("vs. CARSFT (low pressure)",
                   id="vs1-pop",
                   src=IMG_COMPARE1,
                   modal_id="vs1-modal",
                   close_id="vs1-close",
                   description=CAP_1),
        popup_menu("vs. CARSFT (high pressure)",
                   id="vs2-pop",
                   src=IMG_COMPARE2,
                   modal_id="vs2-modal",
                   close_id="vs2-close",
                   description=CAP_2),
    ],
    nav=True,
    in_navbar=True,
    label="Features",
    style={"font-size": "1.2em"}
),

navbar_title = dbc.Container(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url("logo.svg"),
                                     height="32px")),
                    dbc.Col(dbc.NavbarBrand(
                        "CARSpy",
                        className="ml-2 font-weight-bold",
                        style={"font-size": "1.7em"}
                        )
                    ),
                    dbc.Nav(feature_menu, navbar=True)
                ],
                align="center",
                no_gutters=True,
            ),
        ),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.I(
                            title="Intro",
                            className="fas fa-info-circle mr-1",
                            style={"font-size": "1.5em"},
                            id="info-icon"
                        ),
                        popup_modal("Introduction",
                                    description=dcc.Markdown(intro_md),
                                    modal_id="info-modal",
                                    close_id="info-close"),
                    ],
                    id="info-pop",
                    href="#"
                ),
                dbc.NavLink(
                    [
                        html.I(
                            title="Github",
                            className="fab fa-github mr-1",
                            style={"font-size": "1.5em"}
                        ),
                        "",
                    ],
                    href="https://github.com/chuckedfromspace/"
                         + "carspy-dash",
                ),
                dbc.NavLink(
                    [
                        html.I(
                            title="Docs",
                            className="fas fa-book mr-1",
                            style={"font-size": "1.5em"}
                        ),
                        "",
                    ],
                    href="https://carspy.readthedocs.io/"
                ),
                dbc.NavLink(
                    [
                        html.I(
                            title="PyPI",
                            className="fas fa-cubes mr-1",
                            style={"font-size": "1.5em"}
                        ),
                        "",
                    ],
                    href="https://pypi.org/project/carspy/"
                ),
            ],
            className="ml-auto",
            navbar=True
        ),
    ],
    fluid=FLUID_STATE,
),

navbar_tabs = dbc.Container(
    dbc.Tabs(
        [
            dbc.Tab(
                label="Synthesize",
                tab_style={
                    "margin-left": 10,
                },
                activeLabelClassName="border-primary font-weight-bold",
                active_label_style={
                    "background-color": "rgb(240,240,240)",
                    "border-width": "0px 0px 2px 0px",
                    },
            ),
            dbc.Tab(
                label="Least-Square Fit",
                activeLabelClassName="border-primary font-weight-bold",
                active_label_style={
                    "background-color": "rgb(240,240,240)",
                    "border-width": "0px 0px 2px 0px",
                    },
                disabled=True
            ),
        ],
        className="pt-2"
    ),
    fluid=False,
    className="mb-3"
)
navbar = dbc.Container(
    [
        dbc.Navbar(
            navbar_title,
            color="primary",
            dark=True,
        ),
    ],
    fluid=FLUID_STATE,
    className="bg-primary"
)
# Footer
footer = html.Footer(
    [
        dbc.Container(
            [
                html.Hr(),
                html.P("©2021 Zhiyao Yin, German Aerospace Center")
            ],
        )
    ],
    className="p-3 text-center"
)

'''
################################ SYNTH TAB ####################################
'''
# models-tab
range_slider = dbc.FormGroup(
    [
        dbc.InputGroupAddon("Spectral Range [1/cm]"),
        dcc.RangeSlider(id="range", min=2200, max=2400, step=2,
                        value=[2250, 2350],
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
                      "Choose a species", 0),
    synth_mode_select("pump_ls", "pump_ls-addon",
                      "pump_ls-select",
                      ["Gaussian", "Lorentzian"],
                      "Choose a pump laser lineshape", 0),
    synth_mode_select("chi_rs", "chi_rs-addon",
                      "chi_rs-select",
                      ["G-matrix", "isolated"],
                      "Choose a CARS model"),
    synth_mode_select("convol", "convol-addon",
                      "convol-select",
                      ["Kataoka", "Yuratich"],
                      "Choose a convolution method"),
    synth_mode_select("doppler_effect", "doppler-addon",
                      "doppler-select",
                      ["enable", "disable"],
                      "Enable to consider Doppler broadening"),
    input_slider("Pump laser linewdith [1/cm]",
                 "pump_lw-input", 1.01, 0.01, 5, 0.02),
    range_slider
]

# conditions-tab
def make_tab_conditions(P, T):
    tab_conditions = [
        input_slider("Gas pressure [Bar]", "P-input",
                    P, 1.0, 30, 1),
        input_slider("Gas temperature [K]", "T-input",
                    T, 300, 3000, 1),
    ]

    return tab_conditions

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


@app.callback(
    Output("synth-settings-card", "children"),
    Input("synth-settings", "active_tab"),
    State("memory-settings", "data"),
)
def tab_content(active_tab, data):
    if active_tab == "synth-settings-1":
        return make_tab_conditions(data["pressure"],  data["temperature"])
    else:
        return tab_models


@app.callback(
    Output("memory-settings", "data"),
    [
        Input('P-input', 'value'),
        Input('T-input', 'value'),
        State("memory-settings", "data"),
    ]
)
def update_memory(P, T, data):
    data['pressure'] = P
    data['temperature'] = T
    return data


@app.callback(
    Output("synth-signal", "figure"),
    Input("memory-settings", "data")
)
def update_test(data):
    nu, spect = synthesize_cars(**data)
    return plot_cars(nu, spect)


tab_synth = dbc.Row(
    [
        card_setting,
        card_synth
    ],
    className="mb-1",
)
# APP Layout
app.layout = html.Div(
        [
            dcc.Store(
                id="memory-settings",
                data=DEFAULT_SETTINGS
            ),
            navbar,
            navbar_tabs,
            dbc.Container(
                [
                    tab_synth
                ],
                fluid=False
            ),
            footer,
        ],
    )


if __name__ == '__main__':
    app.run_server(debug=True)
