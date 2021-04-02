import numpy as np

from utils_static import *


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



# TODO
avion = {place: id_passager}
if place not in poids:
    # ça veut dire que la place est libre

placements = {id_passager: place}