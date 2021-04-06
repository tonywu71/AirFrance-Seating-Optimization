import numpy as np
import random as rd
import pandas as pd
import re
import json
from numpy.lib.function_base import place
from pandas.io.parsers import read_csv

import plotly.express as px
import plotly.graph_objects as go

from utils_static import *
from utils_dynamic_main import *


def get_list_dates_input():
    """Renvoie la liste des dates des instances fournies dans le dossier "data".
    """

    pattern = '^data_seating_([a-zA-Z0-9]*).csv$'

    # dates_avion est undictionnaire dont les clés sont les dates des instances et
    # dont les clés sont des string donnant l'avion choisi
    list_dates = []

    for filename in os.listdir('data'):
        ans = re.findall(pattern=pattern, string=filename)

        if len(ans) == 1: # Sanity check pour vérifier qu'on a bien une solution...
            list_dates.append(ans[0])

    # Test pour vérifier si on arrive ou non à récupérer des données
    assert len(list_dates) != 0, 'Pas de données correctes trouvées dans le dossier "data" !'

    return list_dates


def get_config_instance(date):
    """Renvoie pour une date et un avion donné la liste des groupes
    et la liste des passagers de l'instance en question.
    """
    ## --- Lecture du CSV ---
    df_instance = read_and_preprocess(date)

    listeGroupes = get_list_groupes(df_instance)
    listePassagers = get_list_passagers(df_instance)

    return listeGroupes, listePassagers


def get_place_proposees_figure(places_proposees, AVION):
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

    for seat_category in preprocess['seats'].keys():
        for couple in preprocess['seats'][seat_category]:
            x,y = couple[0], couple[1]
            avion['seats'][seat_category].append((x,y))      

    ## --- Plot de la figure avec Plotly ---
    if len(places_proposees) == 0:
        fig = px.scatter()
    else:
        fig = px.scatter(
            x= [element[0] for element in places_proposees],
            y= [element[1] for element in places_proposees]
        )

    fig.update_xaxes(range=[0, 37])
    fig.update_yaxes(range=[0.5, 7.5])

    fig.update_traces(mode='markers', marker_line_width=2, marker_size=18, marker_color = 'lightgreen')


    # Add images
    fig.add_layout_image(avion['background']) 

    # Permet de mettre en surbrillance uniquement le point sélectionné
    fig.update_layout(clickmode='event+select')

    # Désactive la possibilité de zoomer
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return fig


## ----- Autres utilitaires -----




def df_to_PI(df, avion):
    """Renvoie un dictionnaire PI de même structure que la variable de décision PI
    Gurobi.

    Args:
        df (DataFrame)

    Returns:
        PI (dict)
    """

    PI = dict()

    list_x_possibles = list(range(avion["x_max"]+2))
    list_y_possibles = list(range(avion["y_max"]+2))

    for idx_passager, row in df.iterrows():


        for x in list_x_possibles:
            for y in list_y_possibles:
                if (x, y) == (row["x"], row["y"]):
                    PI[x, y, idx_passager] = 1
                else:
                    PI[x, y, idx_passager] = 0
    
    return PI

def placements_to_PI_dynamique(placements, avion, date, AVION):
    """Idem que df_to_PI mais avec un dictionnaire "placements" en entrée.

    Args:
        placements (DataFrame)

    Returns:
        PI_dynamique (dict)
    """
    PI_dynamique = dict()

    list_x_possibles = list(range(avion["x_max"]+2))
    list_y_possibles = list(range(avion["y_max"]+2))

    for (id_groupe, idx_passager), (x_passager, y_passager) in placements.items():

        for x in list_x_possibles:
            for y in list_y_possibles:
                if (x_passager, y_passager) == (x, y):
                    PI_dynamique[x, y, get_id_passager(id_groupe, idx_passager, date, AVION)] = 1
                else:
                    PI_dynamique[x, y, get_id_passager(id_groupe, idx_passager, date, AVION)] = 0
    
    return PI_dynamique

def get_id_passager(id_groupe, idx_passager, date, AVION):
    """ Convertir la représentation (id_groupe, idx_passager) en
    la clé unique (id_passager).
    """

    df = pd.read_csv(os.path.join("output", f"solution_{date}_{AVION}.csv"))
    id_passager = df[df['ID Groupe'] == id_groupe].iloc[idx_passager]["ID Passager"]

    return id_passager

def placements_to_passager_places(placements, date, AVION):
    return {get_id_passager(*key, date, AVION): val for key, val in placements.items()}







# Finalement, on préférera shuffle directement dans l'instance pour faire des tests plus facilement.
def get_positions_possibles(id_groupe, idx_passager, date, AVION, listePassagers, listeGroupes, placements, groupe_places, avion, PI_dynamique, limit_options=10):
    """Pour une instance de l'avion (a priori déjà partiellement rempli),
    un groupe donné et un individu de ce groupe (identifié par son idx_passager),
    renvoie une liste de tuples (x, y) donnant les coordonées des places proposées
    à ce même passager.
    """

    print(placements)

    # print(f"idx_passager = {idx_passager}")
    existe_passager_place = (idx_passager > 0)

    passager = listePassagers[get_id_passager(id_groupe, idx_passager, date, AVION)]
    passager_places = placements_to_passager_places(placements, date, AVION)

    print(f"passagers_places = {passager_places}")

    if existe_passager_place: # Si on regarde un autre passager que le premier dans un groupe...
        # intra groupe
        switch_feasible = find_possible_switches_passager(passager, PI_dynamique, passager_places, avion, listePassagers, listeGroupes)
        ALL_SEATS = {}
        for i in range(min(limit_options,len(switch_feasible))):
            x,y = switch_feasible[i][1]
            ALL_SEATS[(x,y)] = switch_feasible[i][0]
        
    
    else : # Si on regarde le 1er passage d'un groupe...
        switch_feasible_inter_groupe = find_possible_switches(id_groupe, PI_dynamique, groupe_places, avion, listePassagers, listeGroupes)
        ALL_SEATS = {}
        for j in range(len(switch_feasible_inter_groupe)):
            switch_feasible = find_possible_switches_passager(passager,switch_feasible_inter_groupe[j][0],passager_places, avion, listePassagers, listeGroupes)
            
            for i in range(min(limit_options,len(switch_feasible))):
                x,y = switch_feasible[i][1]
                ALL_SEATS[(x,y)] = switch_feasible[i][0]



    #places_proposees = list(ALL_SEATS.keys())

    # For debugging only !
    # places_proposees = get_dummy_places_proposees()

    return ALL_SEATS

def get_dummy_places_proposees():
    places_proposees = []

    list_x_possibles = [elt for  elt in range(1, 37) if elt not in [9, 22]]
    list_y_possibles = [elt for elt in range(1, 8) if elt != 4]

    nb_places_proposees = rd.randint(1, 11)
    for _ in range(nb_places_proposees):
        places_proposees.append((np.random.choice(list_x_possibles), np.random.choice(list_y_possibles)))

    return places_proposees


def update_avion(avion, groupe, id_passager, place_choisie):
    """À partir d'une première instance d'objet Avion, d'un groupe donné,
    du passager qu'on traite et enfin de la place choisie par ce dernier,

    Args:
        avion (Avion): instance d'avion à l'étape précédente
        groupe (Groupe): groupe où chercher le passager
        id_passager (int): identifiant du passager (dans le groupe)
        place_choisie ((int, int)): coordonnées x et y de la place choisie

    
    """
    x, y = place_choisie

    ## ----- Update de la place choisie en place occupée -----
    # Etat de la place mis à occupé (dans le code pseudo-vide)
    # TODO

    ## ----- Update du barycentre -----
    # TODO

    return avion

def placements_to_json(placements):
    """Utilitaire pour avoir un dictionnaire avec des strings et non des tuples.
    Permet de debug.
    """
    # print(placements)
    placements_new = {f"({str(key[0])}, {str(key[1])})": f"({str(val[0])}, {str(val[1])})" for key, val in placements.items()}
    return json.dumps(placements_new, indent=2)


def coordToSiege(x, y, AVION):
    gapRangee = 0
    
    if AVION == "A320":
        
        if x > 12:
            gapRangee = 1
            
    elif AVION == "A321":
        
        if x >= 10 and x <= 13:
            gapRangee = -1
        elif x >= 24:
            gapRangee = -1
        
    lettre = ""
    if y == 1:
        lettre = "A"
    elif y == 2:
        lettre = "B"
    elif y == 3:
        lettre = "C"
    elif y == 5:
        lettre = "D"
    elif y == 6:
        lettre = "E"
    elif y == 7:
        lettre = "F" 
    return str(x+gapRangee)+lettre


def placements_to_df(placements, date, AVION):
    """Renvoie le DataFrame associé aux passagers déjà placé et avec
    la même structure que celui déjà construit dans le modèle statique.

    Args:
        placements (dict)
        date (string)
        AVION (string)

    Returns:
        DataFrame
    """
    df_input = read_and_preprocess(date)

    list_categories = ["Femmes", "Hommes", "Enfants", "WCHR"]
    categorie_to_poids = {"Femmes": 65, "Hommes": 80, "Enfants": 35, "WCHR": 70}
    data = []

    if len(placements) == 0:
        df_output = pd.DataFrame(columns=[
            "ID Groupe",
            "ID Passager",
            "Catégorie",
            "Classe",
            "Transit Time",
            "Poids",
            "x",
            "y",
            "Siège"
        ])

    else:
        for id_groupe, row in df_input.iterrows(): # Pour chaque ligne de notre instance de départ...
            idx_passager = 0 # compte le numéro du passager dans le groupe
            
            for categorie in list_categories:
                for _ in range(row[categorie]): # Pour chaque passager du groupe et pour chaque catégorie...
                    
                    if (id_groupe, idx_passager) in placements: # Si le passager en question a déjà été placé...
                        # On récupère les coordonnées de la place choisie :
                        x, y = placements[(id_groupe, idx_passager)]
                        
                        passager_dict = {
                            "ID Groupe": id_groupe,
                            "ID Passager": idx_passager,
                            "Catégorie": categorie.lower() if categorie != 'WCHR' else categorie,
                            "Classe": row["Classe"],
                            "Transit Time": row["TransitTime"],
                            "Poids": categorie_to_poids[categorie],
                            "x": x,
                            "y": y,
                            "Siège": coordToSiege(x, y, AVION)
                        }

                        data.append(passager_dict)
                    
                    else:
                        pass
                        
                    idx_passager += 1

        df_output = pd.DataFrame.from_records(data)
    
    return df_output


def build_df_frequences_size_groupes(date):

    df = pd.readcsv('/data/data_seating_' + date + '.csv')

    df['taille'] = df['Femmes'] + df['Hommes'] + df['Enfants'] + df['WCHR']

    return df.groupby('taille')['Femmes'].count().mean()


def build_table_all_instances(list_dates, build_df_frequences_size_groupes):

    df = pd.DataFrame(columns = ['date', 'value'])

    for date in list_dates:
        value = build_df_frequences_size_groupes(date)
        df_aux = pd.DataFrame({'date': [date], 'value': [value]})
        df = pd.concat([df, df_aux], axis = 0)

    return df
