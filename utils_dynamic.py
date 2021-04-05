import numpy as np
import random as rd
import re
import json

import plotly.express as px
import plotly.graph_objects as go

from utils_static import *


# TODO pour l'avion
# args: liste_groupes, liste_passagers, poids, top_left_corner

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



    ## --- Plot de la figure avec Plotly ---
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


## ----- Classes -----
class Avion:
    """
    Une classe représentant un avion donné avec ses placements déjà réalisés.
    """

    def __init__(self, ref_avion, placements={}):
        """Constructeur pour la classe Avion.

        Args:
            ref_avion (string): "A320" ou "A321"
            placements (dict, optional): de la forme {id_passager: (x_place, y_place)}.
        """
        
        self.ref_avion = ref_avion
        self.placements = placements

    def __str__(self):
        return f'Avion #{self.ref_avion} avec {len(self.placements)} passager(s) déjà placés.'

    def __repr__(self):
        return f'avion #{self.ref_avion} - {len(self.placements)} passager(s) placés'
    
    def is_seat_free(self, place):
        """Renvoie True si et seulement si la place donnée en entrée n'est pas déjà
        occupée.
        """
        return not (place in self.placements)



## ----- Autres utilitaires -----

# Finalement, on préférera shuffle directement dans l'instance pour faire des tests plus facilement.
def get_positions_possibles(avion, groupe, idx_passager):
    """Pour une instance de l'avion (a priori déjà partiellement rempli),
    un groupe donné et un individu de ce groupe (identifié par son idx_passager),
    renvoie une liste de tuples (x, y) donnant les coordonées des places proposées
    à ce même passager.
    Args:
        avion (Avion): instance de l'objet Avion à un certain temps t
        groupe (Groupe): groupe où chercher le passager
        idx_passager (int): identifiant du passager (dans le groupe)
    """
    # Liste de tuples (x, y) donnant les coordonées des places proposées:
    places_proposees = []
    # TODO -> compléter la liste
    places_proposees = get_dummy_places_proposees()

    return places_proposees

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
    print(placements)
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
                            "Catégorie": categorie,
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