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


# args: liste_groupes, liste_passagers, poids, top_left_corner

app = dash.Dash(__name__)


## ------ Obtention de la liste des fichiers de sortie ------
pattern = '^solution_([a-zA-Z0-9]*)_(\w+).csv$'

# dates_avion est undictionnaire dont les clés sont les dates des instances et
# dont les clés sont des string donnant l'avion choisi
dates_avion = dict() 

for filename in os.listdir('output'):
    ans = re.findall(pattern=pattern, string=filename)

    if len(ans) == 1: # Sanity check pour vérifier qu'on a bien une solution...
        date = ans[0][0]
        avion = ans[0][1]
        dates_avion[date] = avion

# Test pour vérifier si on arrive ou non à récupérer des données
assert len(dates_avion) != 0, "Pas de données correctes trouvées dans le dossier data !"

# On extrait les clés du dictionnaire dates_avion pour lire plus facilement les dates:
list_dates = list(dates_avion.keys())






## ------ Widgets ------
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

        html.P(
                    dcc.Markdown( "Visualisation des solutions optimales"),
                    style={
                        'fontSize': 30,
                        'color': '#000099',
                        'text-align': 'left'
                    },
                    className="app__header__title--grey",
                ),

        html.P(
                dcc.Markdown( "Sélectionnez la date pour laquelle vous voulez regarder la solution ci-dessous : "),
                style={
                    'fontSize': 18,
                    'color': 'black',
                    'text-align': 'left'
                },
                className="app__header__title--grey",
            ),
                
    date_dropdown,



     html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("legend2.png"),
                            style={
                                'width': '53%',
                                'position': 'absolute',
                                'left': '5%',
                                'bottom': '3%',
                            },
                            className="app__menu__img",
                        )
                    ],
                    className="app__header__logo",
                ),

    dcc.Graph(id="scatter-plot"),

      html.Div(
                    
                    style={"padding": "100px"}
                    
                ),
])

@app.callback(
    Output("scatter-plot", "figure"), 
    [Input("date-dropdown", "value")])
def update_bar_chart(value):
    ## --- Récupération des données de l'instance sélectionnée dans le Dropdown ---
    date, AVION = value.split("_")

    ## --- Lecture du CSV ---
    filename = f'solution_{date}_{AVION}.csv'
    df_ans = pd.read_csv(os.path.join('output', filename))


    ## --- Calcul du barycentre depuis df_ans directement
    barycentre_x, barycentre_y = calcul_barycentre(df_ans)

    ## --- Récupération des marqueurs pour le tracé dans Plotly
    marker_list = get_markers_passagers(df_ans)

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

    

    # ## Ajout des barres colorées pour visualiser les emplacements spécifiques de l'avion
    # #Issues de Secours
    # fig.add_shape(x0=10.5,
    #             x1=12.5,
    #             y0=0.5,
    #             y1=0.6,
    #             fillcolor="red",
    #             line=dict(width=0),
    #             opacity=0.25)
    # fig.add_shape(x0=10.5,
    #             x1=12.5,
    #             y0=7.4,
    #             y1=7.5,
    #             fillcolor="red",
    #             line=dict(width=0),
    #             opacity=0.25)

    # #Classe Business
    # fig.add_shape(x0=0.5,
    #             x1=9.5,
    #             y0=0.5,
    #             y1=0.6,
    #             fillcolor="orange",
    #             line=dict(width=0),
    #             opacity=0.25)
    # fig.add_shape(x0=0.5,
    #             x1=9.5,
    #             y0=7.4,
    #             y1=7.5,
    #             fillcolor="orange",
    #             line=dict(width=0),
    #             opacity=0.25)

    # #Classe Economie
    # fig.add_shape(x0=9.5,
    #             x1=10.5,
    #             y0=0.5,
    #             y1=0.6,
    #             fillcolor="blue",
    #             line=dict(width=0),
    #             opacity=0.25)
    # fig.add_shape(x0=9.5,
    #             x1=10.5,
    #             y0=7.4,
    #             y1=7.5,
    #             fillcolor="blue",
    #             line=dict(width=0),
    #             opacity=0.25)
    # fig.add_shape(x0=12.5,
    #             x1=28.5,
    #             y0=0.5,
    #             y1=0.6,
    #             fillcolor="blue",
    #             line=dict(width=0),
    #             opacity=0.25)
    # fig.add_shape(x0=12.5,
    #             x1=28.5,
    #             y0=7.4,
    #             y1=7.5,
    #             fillcolor="blue",
    #             line=dict(width=0),
    #             opacity=0.25)


    # Add images
    fig.add_layout_image(avion['background']) 
    return fig

app.run_server(debug=False)