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


# TESTING PURPOSES
list_dates = get_list_dates_input()
date = "7Nov"
AVION = "A321"


# Dicionnaire (global) qui à chaque id_passager associe la place choisie
placements = dict()


# Initialisation de l'instance Avion
# (à ne pas confondre avec AVION qui lui correpond à la référence de l'avion)
avion = Avion(ref_avion=AVION, placements=placements)


# Récupération des données liées à la configuration de l'avion
fig = get_plane_config_graph(date, AVION)
listeGroupes, listePassagers = get_config_instance(date)


# On commence à parcourir le générateur des groupes :
groupe_courant = next(groupe_generator(listeGroupes))


# idx_groupe_courant contiendra le numéro du groupe actuel
idx_groupe_courant = 0

# idem mais avec l'index du passager
idx_passager_courant = 0


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




slider_progress = dcc.Slider(
    id="slider-progress",
    min=0,
    max=len(listeGroupes),
    marks={i: 'Groupe {}'.format(i) for i in range(10)},
    value=idx_groupe_courrant, # vaut 0 a priori au lancement
    disabled=True
)  


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


@app.callback(
    [
        Output('slider-progress', 'value'),
        Output('scatter-plot', 'figure')
    ],
    [
        Input('confirm-button', 'n_clicks'),
        Input(# ajouter le json en sortie du point sélectionné)
    ])
def confirm_action(n_clicks):
    idx_passager_courant += 1 # idx_groupe_courant est une variable globale

    if idx_passager_courant not in listeGroupes[idx_groupe_courant]: # Si on a fini de regarder un groupe...
        idx_groupe_courant += 1
        idx_passager_courant = 0 # On réinitialise le compteur car on commence à explorer un nouveau groupe
    
    places_proposees = get_positions_possibles(avion, groupe_courant, idx_passager_courant) # comment récupérer id_passager ?
    avion = update_avion(avion, groupe_courant, idx_passager_courant, place_choisie) # avion est une variable globale

    return
    #return idx_groupe_courant, fig

    
app.run_server(debug=True)