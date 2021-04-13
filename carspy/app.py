from pathlib import Path
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

ICONS = 'https://use.fontawesome.com/releases/v5.15.3/css/all.css'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO, ICONS])
server = app.server
app.title = 'CARSpy'
FLUID_STATE = True

navbar_title = dbc.Container(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url("logo.svg"),
                                     height="30px")),
                    dbc.Col(dbc.NavbarBrand(
                        "CARSpy",
                        className="ml-2 border-right pr-3 font-weight-bold"
                        )
                    ),
                    dbc.Col(html.Div(
                        "Synthesize and Least-Square Fit Coherent Anti-Stokes "
                        + "Raman Spectra"
                        ),
                        className="ml-1 text-nowrap text-light")
                ],
                align="center",
                no_gutters=True,
            ),
        ),
        dbc.Nav(
            [
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            [
                                html.I(
                                    className="fab fa-github text-white mr-1"
                                ),
                                "Repository",
                            ],
                            href="https://github.com/chuckedfromspace/"
                                 + "carspy-dash")
                    ]
                )
            ],
            className="ml-auto", navbar=True
        ),
    ],
    fluid=FLUID_STATE,
),

app.layout = html.Div([
    html.Div(dbc.Navbar(navbar_title, color="primary", dark=True)),
    html.H2('Hello World'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='display-value')
])

@app.callback(Output('display-value', 'children'),
              [Input('dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)
