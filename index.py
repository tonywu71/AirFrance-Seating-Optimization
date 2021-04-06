import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import app_dynamic_home, app_dynamic_selection


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [
                  Input('url', 'pathname'),
                  Input('confirm-button-1', 'n_clicks')
              ]
              )
def display_page(pathname, n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return app_dynamic_home.layout
    
    else:
        if ctx.triggered[0]["prop_id"] == "confirm-button-1":
            return app_dynamic_selection.layout
        else:
            if pathname == '/app_dynamic_selection':
                return app_dynamic_selection.layout
            else:
                return app_dynamic_home.layout



if __name__ == '__main__':
    app.run_server(debug=True)