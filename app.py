import dash
import dash_bootstrap_components as dbc


class CustomDash(dash.Dash):
    def interpolate_index(self, **kwargs):
        return '''
        <!DOCTYPE html>
        <html>
            <head>
                {metas}
                <meta name="viewport" content="width=device-width,
                initial-scale=1.0" />
                <title>{title}</title>
                {favicon}
                {css}
            </head>
            <body>
                {app_entry}
                {config}
                {scripts}
                {renderer}
            </body>
        </html>
        '''.format(
            metas=kwargs['metas'],
            favicon=kwargs['favicon'],
            title=kwargs['title'],
            app_entry=kwargs['app_entry'],
            config=kwargs['config'],
            scripts=kwargs['scripts'],
            renderer=kwargs['renderer'],
            css=kwargs['css'])


ICONS = 'https://use.fontawesome.com/releases/v5.15.3/css/all.css'
CUSTOM_CSS = "assets/custom.css"
app = CustomDash(__name__,
                 suppress_callback_exceptions=True,
                 external_stylesheets=[dbc.themes.COSMO, ICONS])
app.title = 'CARSpy'
FLUID_STATE = True
