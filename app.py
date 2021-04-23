import dash
import dash_bootstrap_components as dbc

ICONS = 'https://use.fontawesome.com/releases/v5.15.3/css/all.css'
CUSTOM_CSS = "assets/custom.css"
app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.COSMO, ICONS])
app.title = 'CARSpy'
FLUID_STATE = True
