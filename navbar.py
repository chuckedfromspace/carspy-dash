from pathlib import Path
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from app import app
from tab_synthesize import tab_synth
from tab_fit import tab_fit


# callback for collapsing menu
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


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
        # backdrop="static"
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


# generate nav tabs
@app.callback(
    Output("main-content", "children"),
    Input("nav-tabs", "active_tab"),
)
def tab_content(active_tab):
    if active_tab == "nav-tab-synthesize":
        return tab_synth
    elif active_tab == "nav-tab-fit":
        return tab_fit


# load the markdown file
with open(Path(__file__).parent / "README.md", "r") as f:
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
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
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
                        target="_blank",
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
                        target="_blank",
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
                        target="_blank",
                        href="https://pypi.org/project/carspy/"
                    ),
                ],
                className="ml-auto",
                navbar=True
            ),
            id="navbar-collapse",
            navbar=True
        ),
    ],
    fluid=True,
),

navbar_tabs = dbc.Container(
    dbc.Tabs(
        [
            dbc.Tab(
                tab_id="nav-tab-synthesize",
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
                tab_id="nav-tab-fit",
                label="Least-Square Fit",
                activeLabelClassName="border-primary font-weight-bold",
                active_label_style={
                    "background-color": "rgb(240,240,240)",
                    "border-width": "0px 0px 2px 0px",
                    },
            ),
        ],
        id="nav-tabs",
        active_tab="nav-tab-synthesize",
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
    fluid=True,
    className="bg-primary"
)
