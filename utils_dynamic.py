import numpy as np
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
        x= [element[0] for element in places_proposees],
        y= [element[1] for element in places_proposees],
        color = 'green',
    )

    

    # Add images
    fig.add_layout_image(avion['background']) 

    # Permet de mettre en surbrillance uniquement le point sélectionné
    fig.update_layout(clickmode='event+select')
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

## Finalement, on préférera shuffle directement dans l'instance pour faire des tests plus facilement.
# def get_positions_possibles(avion, groupe, id_passager):
#     """Pour une instance de l'avion (a priori déjà partiellement rempli),
#     un groupe donné et un individu de ce groupe (identifié par son id_passager),
#     renvoie une liste de tuples (x, y) donnant les coordonées des places proposées
#     à ce même passager.

#     Args:
#         avion (Avion): instance de l'objet Avion à un certain temps t
#         groupe (Groupe): groupe où chercher le passager
#         id_passager (int): identifiant du passager (dans le groupe)
#     """

#     # Liste de tuples (x, y) donnant les coordonées des places proposées:
#     places_proposees = []

#     # TODO -> compléter la liste


#     return places_proposees

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