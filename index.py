import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from app import app, server
from navbar import navbar, navbar_tabs
from tab_synthesize import tab_synth
from utils import DEFAULT_SETTINGS_CONDITIONS, DEFAULT_SETTINGS_MODELS

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

app.layout = html.Div(
        [
            dcc.Store(
                id="memory-settings-conditions",
                data=DEFAULT_SETTINGS_CONDITIONS
            ),
            dcc.Store(
                id="memory-settings-models",
                data=DEFAULT_SETTINGS_MODELS
            ),
            dcc.Store(
                id="memory-synth-spectrum"
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
