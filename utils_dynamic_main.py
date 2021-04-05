import itertools
from utils_static import calcul_masse_totale_passagers



def voisinage_lateral(x,y, avion):
    """
    Définit le voisinage latéral selon la position du siège.
    """
    if (x,y) in avion['seats']['business']:
        if y == 1:
            return [2]
        elif y == 7:
            return [-2]
        else:
            return [-2, 2]
    else:
        return [-1, 1]




def feasible(PI, avion, listePassagers, listeGroupes):

    '''
    Fonction qui vérifie que les contraintes précédentes sont vérifiées pour pi

    '''

    masseTotalePassagers = sum(passager.poids for passager in listePassagers)
    # TotalePassagers = {masseTotalePassagers}")

    # print(avion)

    # centrage de l'avion
    x_inf = sum(passager.poids*x*PI[x,y,passager.id_passager] for x,y in avion['seats']['real'] for passager in listePassagers) - avion['barycentre'][0]*masseTotalePassagers
    x_sup = -sum(passager.poids*x*PI[x,y,passager.id_passager] for x,y in avion['seats']['real'] for passager in listePassagers)+avion['barycentre'][1]*masseTotalePassagers
    y_inf = sum(passager.poids*y*PI[x,y,passager.id_passager] for x,y in avion['seats']['real'] for passager in listePassagers) - avion['barycentre'][2]*masseTotalePassagers
    y_sup = -sum(passager.poids*y*PI[x,y,passager.id_passager] for x,y in avion['seats']['real'] for passager in listePassagers) + avion['barycentre'][3]*masseTotalePassagers

    if x_inf<0 or x_sup<0 or y_inf<0 or y_sup<0:
        print("cas 1")
        return False

    # sièges fictifs
    delta_fictif = sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['fictive'] for passager in listePassagers)

    if delta_fictif!=0:
        print("cas 2")
        return False

    # au plus un passager par siège

    for x,y in avion['seats']['real']:
        if sum(PI[x,y,passager.id_passager] for passager in listePassagers) > 1:
            print("cas 3")
            return False

    # exactement un siège par passager

    for passager in listePassagers:
        if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['real']) != 1:
            print("cas 4")
            return False

    # pas d'enfant au niveau des issues de secours

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['exit'] for passager in listePassagers if passager.categorie == "enfants") != 0:
        print("cas 5")
        return False

     # pas d'enfant isolé

    for groupe in listeGroupes:
        if listeGroupes[groupe].get_nombre_passagers() <= 1:
            continue
        else:
            nombre_enfants = listeGroupes[groupe].composition['enfants']
            nombre_adultes = listeGroupes[groupe].composition['femmes'] + listeGroupes[groupe].composition['hommes'] + listeGroupes[groupe].composition['WHCR']
            if nombre_enfants >= 1: # s'il y a au moins un enfant...
                for passager in listeGroupes[groupe].list_passagers:
                    if passager.categorie == 'enfants':
                        e = passager.id_passager
                        for x, y in avion['seats']['real']:
                            voisinage = voisinage_lateral(x,y, avion)
                            if nombre_enfants > 2*nombre_adultes:
                                    if sum(PI[x, y+i, passager.id_passager] for i in voisinage for passager in listeGroupes[groupe].list_passagers if passager.id_passager != e) < PI[x, y, e]:
                                        print("cas 6")
                                        return False
                            else:
                                if sum(PI[x, y+i, adulte.id_passager] for i in voisinage for adulte in listeGroupes[groupe].list_passagers if adulte.categorie != 'enfants') < PI[x, y, e]:
                                    print("cas 7")
                                    return False

    # pas de passager Business en classe économique

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['eco'] for passager in listePassagers if passager.classe == "J") != 0 :
        # print("cas 8")
        return False

    # pas de passager économique en classe Business

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['business'] for passager in listePassagers if passager.classe == "Y") != 0 :
        print("cas 9")
        return False

    # contraintes sur les wheelchaires

    val_interdites_y = [1,3,5,7]

    if sum(PI[x,y,w.id_passager] for x,y in avion['seats']['real'] for w in listePassagers if w.categorie == 'WHCR' and y in val_interdites_y) != 0 :
        print("cas 10")
        return False

    for x,y in avion['seats']['real']:
        if y in [2,6]:
            for passager in listePassagers:
                if passager.categorie == 'WHCR':
                    if sum((y == 2) * (PI[x,y+1,p.id_passager] + PI[x-1,y+1,p.id_passager]) + (y == 6) * (PI[x,y-1,p.id_passager] + PI[x-1,y-1,p.id_passager]) + PI[x-1,y,p.id_passager] for p in listePassagers if p.id_passager != passager.id_passager) > 3 * (1 - PI[x,y,passager.id_passager]):
                        print("cas 11")
                        return False

    # contraintes pour les x_max,x_min etc

    return True


###

def find_possible_switches(groupe, PI, groupe_places, avion, listePassagers, listeGroupes): # Calcule toutes les configurations dans lesquelles le groupe 'groupe' peut être échangé avec un autre groupe
    
    switch_feasible = []
    for groupe2 in listeGroupes.keys():
        if groupe2 not in groupe_places:
            # print(f"groupes_places = {groupe_places}")
            if (listeGroupes[groupe].get_nombre_passagers() == listeGroupes[groupe2].get_nombre_passagers() and listeGroupes[groupe].transit_time==listeGroupes[groupe2].transit_time):
                PI_current = {}
                for x in range(avion['x_max']+2):
                    for y in range(avion['y_max']+2):
                        for passager in listePassagers:
                            PI_current[x,y,passager.id_passager]=PI[x,y,passager.id_passager]
                coord1 = []
                coord2 = []
                for x in range(avion['x_max']+2):
                    for y in range(avion['y_max']+2):
                        for p in listeGroupes[groupe].list_passagers:
                            if PI_current[x,y,p.id_passager]==1:
                                coord1.append((x,y,p))
                        for p in listeGroupes[groupe2].list_passagers:
                            if PI_current[x,y,p.id_passager]==1:
                                coord2.append((x,y,p))

                for i in range(len(coord1)):
                    x1 = coord1[i][0]
                    y1 = coord1[i][1]
                    p1 = coord1[i][2]
                    x2 = coord2[i][0]
                    y2 = coord2[i][1]
                    p2 = coord2[i][2]
                    PI_current[x1,y1,p1.id_passager]=0
                    PI_current[x1,y1,p2.id_passager]=1
                    PI_current[x2,y2,p2.id_passager]=0
                    PI_current[x2,y2,p1.id_passager]=1
                # print(f"PI_current = {PI_current}")
                # Maintenant on regarde si cette commutation est faisable
                if feasible(PI_current, avion, listePassagers, listeGroupes):
                    switch_feasible.append((PI_current,coord2))#ne pas faire attention aux p de coord2
    return switch_feasible #contient la configuration de la commutation et la liste des nouvelles coordonnées du groupe

###

def categorie_match(p1,p2):
    cat1 = p1.categorie
    cat2 = p2.categorie

    if cat1=="enfants" and cat2!="enfants":
        return False
    elif cat2=="enfants" and cat1!="enfants":
        return False
    else :
        return True

###

def find_possible_switches_passager(passager, PI, passager_places, avion, listePassagers, listeGroupes): # Calcule toutes les configurations dans lesquelles le groupe 'groupe' peut être échangé avec un autre groupe
    
    switch_feasible = []
    groupe = passager.idx

    for x in range(avion['x_max']+2):
        for y in range(avion['y_max']+2):
            if PI[x,y,passager.id_passager]==1:
                coord1=(x,y)
    for passager2 in listeGroupes[groupe].list_passagers:
        if categorie_match(passager,passager2):
            if passager2.id_passager not in passager_places.keys():
                PI_current = {}
                for x in range(avion['x_max']+2):
                    for y in range(avion['y_max']+2):
                        for passager3 in listePassagers:
                            PI_current[x,y,passager3.id_passager]=PI[x,y,passager3.id_passager]

                for x in range(avion['x_max']+2):
                    for y in range(avion['y_max']+2):
                        if PI_current[x,y,passager2.id_passager]==1:
                            coord2=(x,y)
                x1 = coord1[0]
                y1 = coord1[1]
                x2 = coord2[0]
                y2 = coord2[1]
                PI_current[x1,y1,passager.id_passager]=0
                PI_current[x1,y1,passager2.id_passager]=1
                PI_current[x2,y2,passager2.id_passager]=0
                PI_current[x2,y2,passager.id_passager]=1
                
                # Maintenant on regarde si cette commutation est faisable
                if feasible(PI_current, avion, listePassagers, listeGroupes):
                    switch_feasible.append((PI_current,coord2))

    return switch_feasible #contient la configuration de la commutation et la liste des nouvelles coordonnées du groupe
