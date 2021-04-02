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



## ------ Obtention de la liste des fichiers en entrée ------







## ------ Widgets ------

# Sélecteur d'avion :
avion_dropdown = dcc.Dropdown(
        id='avion-dropdown',
        options=[
            {'label': "A320", 'value': "A320"},
            {'label': "A321", 'value': "A321"}
        ],
        value="A321" # on choisit d'avoir par défaut la 1ère date trouvée
    )

# Sélecteur de date :
date_dropdown = dcc.Dropdown(
        id='date-dropdown',
        options=[
            {'label': f"{date} - {avion}", 'value': f"{date}_{avion}"} for date, avion in dates_avion.items()
        ],
        value=f"{list_dates[0]}_{dates_avion[list_dates[0]]}" # on choisit d'avoir par défaut la 1ère date trouvée
    )



## ------ Layout ------

app.layout = html.Div([
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
        
    ),
        
    # Sélection de date
    html.P(
            dcc.Markdown( "Sélectionnez la date pour de l'instance à charger : "),
            style={
                'fontSize': 18,
                'color': 'black',
                'text-align': 'left'
            },
            className="app__header__title--grey",
        ),   
    date_dropdown,


    # Sélection de l'avion
    html.P(
            dcc.Markdown( "Sélectionnez un avion: "),
            style={
                'fontSize': 18,
                'color': 'black',
                'text-align': 'left'
            },
            className="app__header__title--grey",
        ),   
    avion_dropdown
])

@app.callback(
    Output("scatter-plot", "figure"), 
    [Input("date-dropdown", "value"), Input("avion-dropdown", "value")])
def update_bar_chart(value):
    return

    
app.run_server(debug=True)