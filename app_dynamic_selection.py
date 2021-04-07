## ------ Dash application for visualizing solutions to the dynamic problem ------

import os
import json
import re

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import DashDependency, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from utils_static import *
from utils_dynamic import *

from app import app


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Projet Groupe 2 - AirFrance'
# Car l’usage des tabs crée des components à chaque changement d’onglet :
app.config['suppress_callback_exceptions']=True


# TESTING PURPOSES
list_dates = get_list_dates_input()
date = "17Nov"
AVION = "A321"


# Dicionnaire (global) qui à chaque id_passager associe la place choisie
placements = dict()


listeGroupes, listePassagers = get_config_instance(date)

# print(f"listeGroupes = {listeGroupes}")
# print(f"listePassagers = {listePassagers}")

# idx_groupe_courant contiendra le numéro du groupe actuel
idx_groupe_courant = 0

# Liste qui contient l'ordre de visite des groupes
groupe_courant = listeGroupes[idx_groupe_courant]

# idem mais avec l'index du passager
idx_passager_courant = 0


# groupe_places est une liste qui contient tous les index des groupes complètement placés
groupe_places = []


# Récupération de la variable avion
extension = ""
if len([passager.id_passager for passager in listePassagers if passager.classe == "J"]) == 0:
    extension = "_nb"

with open('./'+AVION+extension+'.json') as f:
    preprocess = json.load(f)
    
avion = {
    'x_max': preprocess['x_max'],
    'y_max': preprocess['y_max'],
    'exit': preprocess['exit'],
    'hallway': preprocess['hallway'],
    'barycentre': preprocess['barycentre'],
    'background': preprocess['background'],
    'seats': {
        'real': [],
        'fictive': [],
        'business': [],
        'exit': [],
        'eco': []        
    }
}

for seat_category in preprocess['seats'].keys():
    for couple in preprocess['seats'][seat_category]:
        x,y = couple[0], couple[1]
        avion['seats'][seat_category].append((x,y))      


# Initialisation de PI à partir de la solution initiale
df_statique = pd.read_csv(os.path.join("output", f"solution_{date}_{AVION}.csv"))
PI_statique = df_to_PI(df_statique, avion)
PI_dynamique = df_to_PI(df_statique, avion)

# Autres variables utiles à initialiser :
placement_dynamique = {} 

# limit_return_intra = nombre de permutations qu'on autorise 'intra groupe'
# limit_return_inter_groupe = nombre de permutations qu'on autorise 'inter groupe'
# limit_return_inter_paquets = nombre de permutations qu'on autorise 'inter paquets'

moyenne_tailles_groupes = build_df_frequences_size_groupes(date)
limit_return_intra, limit_return_inter_groupe, limit_return_inter_paquets = get_params_return_utils(moyenne_tailles_groupes)


# Récupération des données issues de la première itération
ALL_SEATS = get_positions_possibles(idx_groupe_courant, idx_passager_courant, date, AVION, listePassagers, listeGroupes, placements, groupe_places, avion, PI_dynamique, limit_return_intra, limit_return_inter_groupe, limit_return_inter_paquets)
places_proposees = list(ALL_SEATS.keys())
fig = get_place_proposees_figure(places_proposees, AVION)






## ------ Building blocks for Layout ------

# Banderolle de présentation du projet:
div_header = html.Div([
    html.Div(style={"padding": "15px"}),
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
                    'width': '300px',
                    'position': 'absolute',
                    'right': '10px',
                    'top': '75px',
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
                    'width': '250px',
                    'position': 'absolute',
                    'left': '10px',
                    'top': '30px',
                },
                className="app__menu__img",
            )
        ],
        className="app__header__logo",
    ),

    html.Div(
        
        style={"padding": "20px"}
        
    )
])




# Bouton de confirmation du choix de la place :
confirm_button = html.Div([html.Button('Valider', id='confirm-button', type='submit', disabled=True,
    style={
        'margin-left': '600px',
        'margin-bottom': '10px',
        'textAlign':'center',
        'width': '15%',
        'margin':'auto'}
    )], style = {'margin-left': '650px', 'margin-bottom': '20px'}) 
button_finished = html.Button('Regarder la visualisation finale', type='submit', id='button-finished', disabled = False)



loading_spinner = html.Div(
    [
        dcc.Loading(html.Div(id="loading-output"), color = '#000080')
    ]
)


sliders_container = html.Div([

    dcc.Markdown(id = 'update-nombre-groupe'),

    dcc.Slider(
        id="slider-groupe",
        min=0,
        max=len(listeGroupes),
        marks={idx: f'{idx}'for idx in range(len(listeGroupes))  if idx % 10 == 0},
        value=idx_groupe_courant, # vaut 0 a priori au lancement
        disabled=True,
        persistence=True
    ),

    dcc.Markdown(id = 'update-nombre-passager'),

    dcc.Slider(
        id="slider-passager",
        min=0,
        max=len(listeGroupes[idx_groupe_courant].list_passagers),
        # marks={idx: f'Passager {str(passager.idx)}'for idx, passager in enumerate(listeGroupes[idx_groupe_courant].list_passagers)},
        value=idx_passager_courant, # vaut 0 a priori au lancement
        disabled=True,
        persistence=True
    )
], id = 'div-sliders', style = { 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto'})

# Figure Plotly où on sélectionnera les places pour chaque passager :
scatter_plot = html.Div([
    dcc.Graph(
        id="scatter-plot",
        figure=fig,
        config={"displayModeBar": False, "showTips": False},
        )
]) 


finished_phrase = html.H3(
    "Vous avez fini de placer les passagers!", style = {'color': '#990000', 'text-align':'center'}, id = 'finished-phrase'
)


text_date = html.Div([html.H5(f"Airbus {AVION} / {date}")], style = {'color': '#990000', 'text-align':'center'}, id = 'date')





## ------ Defining Tab ------
tab_1 = dcc.Tab(
                label='Sélection des places',
                value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected'
            )

tab_2 = dcc.Tab(
                label='Prévisualisation',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected'
            )


## ------ Defining Tab Contents ------
tab_1_content = html.Div([
    
    text_date,
    sliders_container,
    scatter_plot,
    # debug_clickData,
    confirm_button,
    loading_spinner,
    html.Div(style={"padding": "25px"}),
    # debug_placements,
    

])

tab_2_content = html.Div([
    html.H5(f"Airbus {AVION} / {date}"),
    dcc.Graph(id="result-preview"),
     html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("legend-dynamique.png"),
                            style={
                                'width': '53%',
                                'position': 'absolute',
                                'left': '5%',
                                'bottom': '2%',
                            },
                            className="app__menu__img",
                        )
                    ],
                    className="app__header__logo",
                ),
        html.Div(style={"paddding": "15px"})

])


## ------ Defining Layout ------
app.layout = html.Div([
    div_header, # Banderolle de présentation du projet
    dcc.Tabs(
        id="tabs",
        value='tab-1',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            tab_1,
            tab_2
        ],
        persistence=True),

    html.Div(id='tabs-content-classes', style={"justify-content": 'space-around'},),

    html.Div([finished_phrase], style={ 'margin-left': '450px','verticalAlign': 'middle', 'display': 'none'}),
    html.Div([button_finished,], style={'margin-left': '550px', 'margin-bottom': '10px','verticalAlign': 'middle', 'display': 'none'}),

    html.Div([
    dcc.Markdown(f"""
                **{date}_{AVION}**
            """),
    dcc.Graph(id="finished-graph")

], id = "finished-graph-holder", style = {'display': 'none'})

])



## ------ Callbacks (tabs) ------
@app.callback(Output('tabs-content-classes', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab_1_content
    elif tab == 'tab-2':
        return tab_2_content


## ------ Callbacks - Tab 1 ------
# @app.callback(
#     Output('click-data', 'children'),
#     Input('scatter-plot', 'clickData'))
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)

@app.callback(
    Output('confirm-button', 'disabled'),
    Input('scatter-plot', 'clickData')
    )
def is_point_selected(clickData):
    return clickData is None

# first_it = True #flag first it 

@app.callback(
    [
        Output('slider-passager', 'value'),
        Output('update-nombre-passager', 'children'),
        Output('update-nombre-groupe', 'children'),
        Output('slider-passager', 'max'),
        # Output('slider-passager', 'marks'),
        Output('slider-groupe', 'value'),
        Output('scatter-plot', 'figure'),
        # Output('debug-placements', 'children'),
        Output('scatter-plot', 'clickData'),
        Output("loading-output", "children"),
        Output(component_id='div-sliders', component_property='style'),
        Output(component_id='confirm-button', component_property='style'),
        Output(component_id='scatter-plot', component_property='style'),
        # Output(component_id='debug-placements', component_property='style'),
        # Output(component_id='click-data', component_property='style'),
        Output(component_id='date', component_property='style'),
        Output(component_id='tabs', component_property='style'),
        Output(component_id='tabs-content-classes', component_property='style'),
        Output(component_id='finished-phrase', component_property='style'),
        Output(component_id='button-finished', component_property='style'),
 
    ],
    Input('confirm-button', 'n_clicks'),
    State('scatter-plot', 'clickData'))
def confirm_action(n_clicks, clickData):
    global placements, places_proposees, idx_groupe_courant, idx_passager_courant, date, AVION, finish, groupe_places, PI_dynamique, ALL_SEATS, limit_return_intra, limit_return_inter_groupe, limit_return_inter_paquets
    
    if  idx_groupe_courant < len(listeGroupes) - 1:
        if n_clicks is not None:
            
            

            place_choisie = (clickData["points"][0]["x"], clickData["points"][0]["y"])
            
            
            
            # Mise à jour du dictionnaire placements :
            placements[idx_groupe_courant, idx_passager_courant] = place_choisie
            placements_json = placements_to_json(placements)
            groupe_places.append(idx_groupe_courant)

            # if first_it:
            #     idx_groupe_courant -= 1 #mettre premier groupe à 0
            #     first_it = False 


            print(f"idx_groupe_courant = {idx_groupe_courant}")
            print(f"idx_passager_courant = {idx_passager_courant}")
            print()

            print(f"groupe_places = {groupe_places}")

            # Mise à jour du PI_dynamique
            x, y = place_choisie
            PI_dynamique = ALL_SEATS[x, y]

            idx_passager_courant += 1 # idx_groupe_courant est une variable globale

            if idx_passager_courant not in list(range(len(listeGroupes[idx_groupe_courant].list_passagers))): # Si on a fini de regarder un groupe...
                idx_groupe_courant += 1
                idx_passager_courant = 0 # On réinitialise le compteur car on commence à explorer un nouveau groupe

            
            ALL_SEATS = get_positions_possibles(idx_groupe_courant, idx_passager_courant, date, AVION, listePassagers, listeGroupes, placements, groupe_places, avion, PI_dynamique, limit_return_intra, limit_return_inter_groupe, limit_return_inter_paquets)
            places_proposees = list(ALL_SEATS.keys())
            # print(f"places_proposees = {places_proposees}")

            

            


        else:
            ALL_SEATS = get_positions_possibles(idx_groupe_courant, idx_passager_courant, date, AVION, listePassagers, listeGroupes, placements, groupe_places, avion, PI_dynamique, limit_return_intra, limit_return_inter_groupe, limit_return_inter_paquets)
            places_proposees = list(ALL_SEATS.keys())
            # print(f"places_proposees = {places_proposees}")
            placements_json = str()
            pass
        
        # avion = update_avion(avion, groupe_courant, idx_passager_courant, place_choisie) # avion est une variable globale
        fig = get_place_proposees_figure(places_proposees, AVION)
        
        # Mise à jour des sliders :
        listePassagers_courant = listeGroupes[idx_groupe_courant].list_passagers
        max_slider_passager = len(listePassagers_courant)
        marks_slider_passager = {idx: f'Passager {str(passager.idx)}' for idx, passager in enumerate(listePassagers_courant)},
        # NB: On profite de regénérer la figure pour désélectionner le point précédent !

        str_passager = f"""
                **Passager {idx_passager_courant} du groupe courant**
            """ 

        str_groupe = f"""
                **Groupe {idx_groupe_courant}**
            """

        return idx_passager_courant,str_passager, str_groupe, max_slider_passager, idx_groupe_courant, fig, None,'', {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'},{'display': 'block'}, {'display': 'block'},{'display': 'none'}, {'display': 'none'}

    else:
        str_passager = f"""
                **Passager 0 du groupe courant**
            """

        str_groupe = f"""
                **Groupe 0**
            """

        return 0, str_passager,str_groupe, 0, 0, px.scatter(), None, '', {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'},{'display': 'none'}, {'display': 'block'}, {'display': 'block'}



@app.callback(
    [Output(component_id='finished-graph-holder', component_property='style'),
     Output("finished-graph", "figure")], 
    Input('button-finished', 'n_clicks')
    )

def display_finish_graph(n_clicks):

    ## --- Récupération des données de l'instance sélectionnée dans le Dropdown ---
    global placements, date, AVION

    df_ans = placements_to_df(placements, date, AVION)


    ## --- Calcul du barycentre depuis df_ans directement
    if len(df_ans) == 0:
        barycentre_x, barycentre_y =  18.5, 4
    else:
        barycentre_x, barycentre_y = calcul_barycentre(df_ans)

    ## --- Récupération des marqueurs pour le tracé dans Plotly
    marker_list = get_markers_passagers(df_ans)
    print(df_ans)

    ## --- Récupération de certaines métadonnées nécessaire à Plotly
    with open('./'+AVION+'.json') as f:
        preprocess = json.load(f)
    
    avion = {
        'x_max': preprocess['x_max'],
        'y_max': preprocess['y_max'],
        'exit': preprocess['exit'],
        'hallway': preprocess['hallway'],
        'barycentre': preprocess['barycentre'],
        'background': preprocess['background'],
        'seats': {
            'real': [],
            'fictive': [],
            'business': [],
            'exit': [],
            'eco': []        
        }
    }

    ## --- Plot de la figure avec Plotly ---
    if len(df_ans) == 0:
        fig = px.scatter()
    else:
        fig = px.scatter(
            df_ans,
            x='x',
            y='y',
            hover_name='Siège',
            color= 'ID Groupe',
            size='Poids',
            hover_data=df_ans.columns,
            template="plotly_white",
            color_continuous_scale=px.colors.diverging.RdBu)


    fig.update_xaxes(range=[0, 37])
    fig.update_yaxes(range=[0.5, 7.5])

     

    fig.update_traces(marker=dict(line=dict(width=2, color='black')),
                    marker_symbol=marker_list,
                    selector=dict(mode='markers'))


    ## Ajout du barycentre
    fig.add_trace(
        go.Scatter(x=[barycentre_x],
                y=[barycentre_y],
                name="Barycentre",
                showlegend=False,
                marker_symbol=["star-triangle-up-dot"],
                mode="markers",
                marker=dict(size=20,
                            color="green",
                            line=dict(width=2, color='DarkSlateGrey'))))

    fig.add_layout_image(source=f"cabine{AVION}AF.jpg")


    # Positionnement de la légende
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    # Add images
    fig.add_layout_image(avion['background']) 

    if n_clicks is not None:
        return {'display': 'block'}, fig
    return{'display': 'none'}, fig
 





## ------ Callbacks - Tab 2 ------
@app.callback(
    Output("result-preview", "figure"), 
    Input('tabs', 'value'))
def update_preview(n_clicks):
    ## --- Récupération des données de l'instance sélectionnée dans le Dropdown ---
    global placements, date, AVION, avion

    df_ans = placements_to_df(placements, date, AVION)
    df_ans = df_ans.astype({"Time Transit": str})


    ## --- Calcul du barycentre depuis df_ans directement
    if len(df_ans) == 0:
        barycentre_x, barycentre_y =  18.5, 4
    else:
        barycentre_x, barycentre_y = calcul_barycentre(df_ans)

    ## --- Récupération des marqueurs pour le tracé dans Plotly
    marker_list = get_markers_passagers(df_ans)

    ## --- Récupération de certaines métadonnées nécessaire à Plotly
    extension = ""
    if len([passager.id_passager for passager in listePassagers if passager.classe == "J"]) == 0:
        extension = "_nb"
    with open('./'+AVION+extension+'.json') as f:
        preprocess = json.load(f)
    
    avion = {
        'x_max': preprocess['x_max'],
        'y_max': preprocess['y_max'],
        'exit': preprocess['exit'],
        'hallway': preprocess['hallway'],
        'barycentre': preprocess['barycentre'],
        'background': preprocess['background'],
        'seats': {
            'real': [],
            'fictive': [],
            'business': [],
            'exit': [],
            'eco': []        
        }
    }

    for seat_category in preprocess['seats'].keys():
        for couple in preprocess['seats'][seat_category]:
            x,y = couple[0], couple[1]
            avion['seats'][seat_category].append((x,y))      

    ## --- Plot de la figure avec Plotly ---
    if len(df_ans) == 0:
        fig = px.scatter()
    else:
        fig = px.scatter(
            df_ans,
            x='x',
            y='y',
            hover_name='Siège',
            color= 'ID Groupe',
            size='Poids',
            hover_data=df_ans.columns,
            template="plotly_white",
            color_continuous_scale=px.colors.diverging.RdBu)


    fig.update_xaxes(range=[0, 37])
    fig.update_yaxes(range=[0.5, 7.5])

    fig.update_traces(marker=dict(line=dict(width=2, color='black')),
                    marker_symbol=marker_list,
                    selector=dict(mode='markers'))


    ## Ajout du barycentre

    # Couleur pour le point représentant le barycentre selon sa position
    if avion['barycentre'][1] >= barycentre_x >= avion['barycentre'][0] and avion['barycentre'][3] >= barycentre_y >= avion['barycentre'][2]:
        color = "green"
        legende_barycentre = "Barycentre"
    else:
        color = "red"
        legende_barycentre = "Barycentre (non centré)"

    fig.add_trace(
        go.Scatter(x=[barycentre_x],
                y=[barycentre_y],
                name=legende_barycentre,
                showlegend=True,
                marker_symbol=["star-triangle-up-dot"],
                mode="markers",
                marker=dict(size=20,
                            color=color,
                            line=dict(width=2, color='DarkSlateGrey'))))

    fig.add_layout_image(source=f"cabine{AVION}AF.jpg")


    # Positionnement de la légende
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    # Add images
    fig.add_layout_image(avion['background']) 
    return fig


app.run_server(debug=False)