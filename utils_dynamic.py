import numpy as np
import re

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
            list_dates.append(ans[0][0])

    # Test pour vérifier si on arrive ou non à récupérer des données
    assert len(list_dates) != 0, 'Pas de données correctes trouvées dans le dossier "data" !'

    return list_dates





## ----- Classes -----
class Avion:
    """
    Une classe représentant un avion donné avec ses placements déjà réalisés.
    """

    def __init__(self, ref_avion, placements={}):
        """Constructeur pour la classe Avion.

        Args:
            ref_avion (string): "A320" ou "A321"
            placements (dict, optional): de la forme {id_passager: (x_place, y_palce)}.
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
def groupe_generator(liste_groupes):
    """Générateur pour parcourir simplement tous les groupes d'une instance
    de manière aléatoire

    Args:
        liste_groupes (list of Groupe)  

    Yields:
        Groupe
    """
    while len(liste_groupes) != 0:
        n = len(liste_groupes)
        groupe_courrant = liste_groupes.pop(np.random.randint(0, n))
        # NB : np.random.randint renvoie un nombre entre 0 et n exlus

        yield groupe_courrant



def get_positions_possibles(avion, groupe, id_passager):
    """Pour une instance de l'avion (a priori déjà partiellement rempli),
    un groupe donné et un individu de ce groupe (identifié par son id_passager),
    renvoie une liste de tuples (x, y) donnant les coordonées des places proposées
    à ce même passager.

    Args:
        avion (Avion): instance de l'objet Avion à un certain temps t
        groupe (Groupe): groupe où chercher le passager
        id_passager (int): identifiant du passager (dans le groupe)
    """

    # Liste de tuples (x, y) donnant les coordonées des places proposées:
    places_proposees = []

    # TODO -> compléter la liste


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