import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from app import app
from navbar import navbar, navbar_tabs
from tab_synthesize import tab_synth
from utils import DEFAULT_SETTINGS

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
