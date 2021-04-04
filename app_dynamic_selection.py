## ------ Dash application for visualizing solutions to the dynamic problem ------

import os
import json
import re

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from utils_static import *
from utils_dynamic import *


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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

listeGroupes, listePassagers = get_config_instance(date)

# idx_groupe_courant contiendra le numéro du groupe actuel
idx_groupe_courant = 0

# Liste qui contient l'ordre de visite des groupes
groupe_courant = listeGroupes[idx_groupe_courant]

# idem mais avec l'index du passager
idx_passager_courant = 0

# Récupération des données issues de la première itération
places_proposees = get_positions_possibles(avion, groupe_courant, idx_passager_courant)
fig = get_place_proposees_figure(places_proposees, AVION)





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
debug_clickData = html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),

            html.Pre(id='click-data')
        ], className='three columns')


# Bouton de confirmation du choix de la place :
confirm_button = html.Button('Valider', id='confirm-button', type='submit', disabled=True)


sliders_container = html.Div([

    
    dcc.Markdown("""
                **Groupe**
            """),

    dcc.Slider(
        id="slider-groupe",
        min=0,
        max=len(listeGroupes),
        marks={idx: f'{idx}'for idx in range(len(listeGroupes))  if idx % 10 == 0},
        value=idx_groupe_courant, # vaut 0 a priori au lancement
        disabled=True,
    ),

    dcc.Markdown("""
                **Passager**
            """),

    dcc.Slider(
        id="slider-passager",
        min=0,
        max=len(listeGroupes[idx_groupe_courant].list_passagers),
        marks={idx: f'Passager {str(passager.idx)}'for idx, passager in enumerate(listeGroupes[idx_groupe_courant].list_passagers)},
        value=idx_passager_courant, # vaut 0 a priori au lancement
        disabled=True
    )
],  style = { 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto'})

# Figure Plotly où on sélectionnera les places pour chaque passager :
scatter_plot = dcc.Graph(
        id="scatter-plot",
        figure=fig,
        config={"displayModeBar": False, "showTips": False}
        )


# Component de debug pour afficher les infos du point sélectionné :
debug_clickData = html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),

            html.Pre(id='click-data')
        ], className='three columns')

debug_placements = html.Pre(id='debug-placements')


## ------ Defining Layout ------
app.layout = html.Div([
    div_header, # Banderolle de présentation du projet

    dcc.Markdown(f"""
                **{date}_{AVION}**
            """),
    sliders_container,
    scatter_plot,
    debug_clickData,
    confirm_button,
    debug_placements
])






@app.callback(
    Output('click-data', 'children'),
    Input('scatter-plot', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('confirm-button', 'disabled'),
    Input('scatter-plot', 'clickData')
    )
def is_point_selected(clickData):
    return clickData is None

first_it = True #flag first it 

@app.callback(
    [
        Output('slider-passager', 'value'),
        Output('slider-passager', 'max'),
        # Output('slider-passager', 'marks'),
        Output('slider-groupe', 'value'),
        Output('scatter-plot', 'figure'),
        Output('debug-placements', 'children')
    ],
    Input('confirm-button', 'n_clicks'),
    State('scatter-plot', 'clickData'))

def confirm_action(n_clicks, clickData):
    global placements, places_proposees, idx_groupe_courant, idx_passager_courant, date, AVION, first_it

    if n_clicks is not None:
        idx_passager_courant += 1 # idx_groupe_courant est une variable globale
        

        place_choisie = (clickData["points"][0]["x"], clickData["points"][0]["y"])
        print('debugei')
        print(list(range(len(listeGroupes[idx_groupe_courant].list_passagers))))
        print(idx_groupe_courant)
        if idx_passager_courant not in list(range(len(listeGroupes[idx_groupe_courant].list_passagers))): # Si on a fini de regarder un groupe...
            idx_groupe_courant += 1
            idx_passager_courant = 0 # On réinitialise le compteur car on commence à explorer un nouveau groupe
        
        if first_it:
            idx_groupe_courant -= 1 #mettre premier groupe à 0
            first_it = False 


        print(f"idx_groupe_courant = {idx_groupe_courant}")
        print(f"idx_passager_courant = {idx_passager_courant}")
        print()

        
        places_proposees = get_positions_possibles(avion, groupe_courant, idx_passager_courant)
        print(places_proposees)

        # Mise à jour du dictionnaire placements :
        placements[idx_groupe_courant, idx_passager_courant] = place_choisie
        placements_json = placements_to_json(placements)


    else:
        places_proposees = get_positions_possibles(avion, groupe_courant, idx_passager_courant)
        print(places_proposees)
        placements_json = str()
        pass
    
    # avion = update_avion(avion, groupe_courant, idx_passager_courant, place_choisie) # avion est une variable globale
    fig = get_place_proposees_figure(places_proposees, AVION)
    
    # Mise à jour des sliders :
    listePassagers_courant = listeGroupes[idx_groupe_courant].list_passagers
    max_slider_passager = len(listePassagers_courant)
    marks_slider_passager = {idx: f'Passager {str(passager.idx)}' for idx, passager in enumerate(listePassagers_courant)},
    # NB: On profite de regénérer la figure pour désélectionner le point précédent !

 

    return idx_passager_courant, max_slider_passager, idx_groupe_courant, fig, placements_json

    
app.run_server(debug=True)