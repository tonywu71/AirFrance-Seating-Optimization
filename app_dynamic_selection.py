## ------ Dash application for visualizing solutions to the dynamic problem ------

import os
import json
import re

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

from utils_static import *
from utils_dynamic import *



app = dash.Dash(__name__)

placements = dict()



# TESTING PURPOSES
list_dates = get_list_dates_input()
date = "7Nov"
AVION = "A321"

fig = get_plane_config_graph(date, AVION)
# listeGroupes, listePassagers = get_config_instance(date)



idx_groupe_courrant = 0


## ------ Building blocks for Layout ------

# Banderolle de présentation du projet:
div_header = html.Div([
    html.Div(
        [
            html.H1("Projet AirFrance (ST7) - Groupe 2", className="app__header__title", style = {'color': '#990000', 'text-align':'center'}),
            html.P(
                dcc.Markdown( "Caio Iglesias, Thomas Melkior, Quentin Guilhot, Tony Wu, Thomas Bouquet"),
                style={
                    'fontSize': 16,
                    'color': '#990000',
                    'text-align':'center'
                },
                className="app__header__title--grey",
            ),
        ],
        className="app__header__desc",

    ),

    html.Div(
        [
            html.Img(
                src=app.get_asset_url("AirFrance_logo.png"),
                style={
                    'width': '20%',
                    'position': 'absolute',
                    'right': '4%',
                    'top': '6%',
                },
                className="app__menu__img",
            )
        ],
        className="app__header__logo",
    ),

    html.Div(
        [
            html.Img(
                src=app.get_asset_url("cs_logo.png"),
                style={
                    'width': '13%',
                    'position': 'absolute',
                    'right': '85%',
                    'top': '2%',
                },
                className="app__menu__img",
            )
        ],
        className="app__header__logo",
    ),

    html.Div(
        
        style={"padding": "10px"}
        
    )
])



# Textbox pour débugger :
debug_textbox = html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),
            html.Pre(id='click-data')
        ], className='three columns')


# Bouton de confirmation du choix de la place :
confirm_button = html.Button('Valider', id='confirm-button', type='submit', disabled=True)




# slider_progress = dcc.Slider(
#     id="slider-progress",
#     min=0,
#     max=len(listeGroupes),
#     marks={i: 'Groupe {}'.format(i) for i in range(10)},
#     value=idx_groupe_courrant,
#     disabled=True
# )  


## ------ Defining Layout ------
app.layout = html.Div([
    div_header, # Banderolle de présentation du projet

    dcc.Graph(
        id="scatter-plot",
        figure=fig,
        config={"displayModeBar": False, "showTips": False}
        ),
    debug_textbox,
    confirm_button
])






@app.callback(
    Output('click-data', 'children'),
    Input('scatter-plot', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

@app.callback(
    Output('confirm-button', 'disabled'),
    Input('scatter-plot', 'clickData'))
def is_point_selected(clickData):
    return clickData is None


    
app.run_server(debug=True)