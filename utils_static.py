import os
from typing import Generator
import pandas as pd


## ------- Pour l'importation des données -------
def read_and_preprocess(date):
    """Renvoie le DataFrame correspondant à l'instance
    à la date donnée.
    """
    df = pd.read_csv(get_filepath(date))

    # Conversion en TimeStamp
    df['TransitTime'] = pd.to_datetime(df['TransitTime']).dt.time

    return df

def get_filepath(date, data_source='data'):
    """Renvoie le filepath d'un fichier donné 

    Args:
        date (string): string contenant la date sous
            le format {jour}{Mois abbrégé}
            -> exemple : 7Nov

    Returns:
        string
    """
    return os.path.join(data_source, f'data_seating_{date}.csv')



## ------- Classes -------

class Passager:
    
    """
    Une classe représentant un passager et toutes les données qui lui sont associées. 
    """
    
    def __init__(self, idx, id_passager, categorie, classe, transit_time=0):
        
        """
        Constructeur pour la classe Passager.
        
        Args:
            idx (int): Indice du groupe dans le fichier Excel
            categorie (Categories): Catégorie du passager (Femme, Homme, Enfant, Fauteil Roulant)
            classe (Classes): Lettre donnant la classe du passager
            transit_time (string, optional): String au format %H:%M:%S donnat le
                temps de transit pour le passager. Defaults to 0.
        """
        
        self.idx = idx
        self.id_passager = id_passager
        self.categorie = categorie
        self.classe = classe
        self.transit_time = transit_time
        self.poids()
    
    def __str__(self):
        return f'Passager # {self.id_passager}, catégorie {self.categorie} du groupe #{self.idx}, classe {self.classe} et temps de correspondance de {self.transit_time}'
    
    def __repr__(self):
        return f'passager # {self.id_passager} du groupe #{self.idx}'          
    
    def poids(self):
        """
        Définit le poids du passager selon sa catégorie.
        """
        
        global numFemme, numHomme, numWHCR, numEnfant
        
        # Pour chaque passager, on modifie très légèrement le poids pour "briser" la symétrie
        
        if self.categorie == "femmes":
            self.poids = 65 + numFemme / 100
            numFemme += 1
        elif self.categorie == "hommes":
            self.poids = 80 + numHomme / 100
            numHomme += 1
        elif self.categorie == "WHCR":
            self.poids = 70 + numWHCR / 100
            numWHCR += 1
        else:
            self.poids = 35 + numEnfant / 100
            numEnfant += 1

class Groupe:
    
    """
    Une classe représentant un groupe de passagers ayant réservé leur places d'avion ensemble. 
    Un groupe correspond donc à une ligne dans le fichier Excel de départ.
    """

    def __init__(self, idx, nb_femmes, nb_hommes, nb_enfants, nb_WCHR, classe, transit_time=0):
        
        """
        Constructeur pour la classe Groupe.
        
        Args:
            idx (int): Indice du groupe dans le fichier Excel
            nb_femmes (int): Nombre de femmes dans le groupe
            nb_hommes (int): Nombre d'hommes dans le groupe
            nb_enfants (int): Nombre d'enfants dans le groupe
            nb_WCHR (int): Nombre de personnes handicapés dans le groupe
            classe (Classes): Lettre donnant la classe du groupe
            transit_time (string, optional): String au format %H:%M:%S donnat le
                temps de transit pour le groupe. Defaults to 0.
        """
        
        self.idx = idx
        self.composition = {
            'femmes': nb_femmes,
            'hommes': nb_hommes,
            'enfants': nb_enfants,
            'WHCR': nb_WCHR
        }
        self.classe = classe
        self.transit_time = transit_time

        self.list_passagers = []
        global numPassager

        for categorie in self.composition.keys():
            for nbParCategorie in range(self.composition[categorie]):
                self.list_passagers.append(Passager(
                    self.idx,
                    numPassager,
                    categorie,
                    self.classe,
                    self.transit_time))
                numPassager += 1   

        return

    def __str__(self):
        return f'Groupe #{self.idx} avec {self.get_nombre_passagers()} passager(s), classe {self.classe} et temps de correspondance de {self.transit_time}'

    def __repr__(self):
        return f'groupe #{self.idx}'
    
    def iter_passagers(self):
        """Générateur pour la liste des passagers dans le groupe.
        Yields:
            Passager: instance de la classe Passager
        """
        for passager in self.list_passagers:
            yield passager

    def est_seul(self):
        """Renvoie True si le groupe contient un seul
        passager et False sinon.
        """
        return len(self.list_passagers) == 1
    
    def get_nombre_passagers(self):
        """Renvoie le nombre de passagers dans le groupe considéré.
        """
        return len(self.list_passagers)

    def comprend_enfants(self):
        """Renvoie True si le groupe contient au moins un enfant
        en son sein et False sinon.
        """
        return any([passager.categorie == 'enfants' for passager in self.list_passagers])      


## ------- Utilitaires pour les classes -------
def string_to_min(date):
    
    """
    Fonction qui transforme une heure au format HH:MM:SS 
    en l'entier correspondant au nombre de minutes de cette dernière.
    """
    
    hms = date.split(":")
    if date == "00:00:00":
        return float('inf')
    else:
        return int(60*int(hms[0]) + int(hms[1]) + int(hms[2])*50/3)


def get_list_groupes(df):
    """Renvoie une liste qui à chaque index de groupe
    renvoie un objet Groupe donnant sa composition.
    """
    listeGroupes = []

    for idx, row in df.iterrows():

        listeGroupes[idx] = Groupe(
            idx=idx,
            nb_femmes=row['Femmes'],
            nb_hommes=row['Hommes'],
            nb_enfants=row['Enfants'],
            nb_WCHR=row['WCHR'],
            classe=row['Classe'],
            transit_time=string_to_min(str(row['TransitTime']))
        )
    
    return listeGroupes

def get_list_passagers(df):
    """Renvoie une liste qui à chaque index de groupe
    renvoie une liste de ses passagers.
    """
    # Liste des groupes
    listeGroupes = get_list_groupes(df)

    # Liste des passagers, récupérée via la liste des groupes
    listePassagers = []

    for groupe in listeGroupes.keys():
        listePassagers += listeGroupes[groupe].list_passagers  

    return listePassagers


## ------- Pour récupérer des informations sur les solutions pré-calculées -------
def calcul_masse_totale_passagers(df_ans):
    """Renvoie la masse totale de tous les passagers d'une instance.

    Args:
        df_ans (DataFrame): DataFrame renvoyé par la fonction exporter_resultats
            définie dans le notebook

    Returns:
        float
    """
    return df_ans['Poids'].sum()

def calcul_barycentre(df_ans):
    """Renvoie un tuple donnant les coordonnées du barycentre dans le plan de l'avion.

    Args:
        df_ans (DataFrame): DataFrame renvoyé par la fonction exporter_resultats
            définie dans le notebook

    Returns:
        (barycentre_x, barycentre_y) où barycentre_x et barycentre_y sont des floats
    """
    # Calcul de la masse totale des passagers
    masse_totale_passagers = calcul_masse_totale_passagers(df_ans)
    
    poids_x = 0
    poids_y = 0
    
    for idx, passager in df_ans.iterrows(): # passager est une ligne de notre DataFrame
        poids_x += passager['x'] * passager['Poids']
        poids_y += passager['y'] * passager['Poids']
    
    barycentre = (poids_x / masse_totale_passagers, poids_y / masse_totale_passagers)
    
    return barycentre

def get_markers_passagers(df_ans):
    """Renvoie la liste marker_list à donner en argument lors du tracé Plotly
    pour plus facilement identifier les passagers.

    Args:
        df_ans (DataFrame): DataFrame renvoyé par la fonction exporter_resultats
            définie dans le notebook

    Returns:
        list
    """
    marker_list = []

    for idx, passager in df_ans.iterrows():
        if passager["Classe"] == "Business":
            dot = "-dot"
        else:
            dot = ""
        if passager["Catégorie"] == "femmes":
            marker_list.append('circle'+dot)    
        elif passager["Catégorie"] == "hommes":
            marker_list.append('hexagon'+dot)
        elif passager["Catégorie"] == "enfants":
            marker_list.append('star'+dot)   
        elif passager["Catégorie"] == "WHCR":
            marker_list.append('star-square'+dot)
    
    return marker_list