import itertools
from utils_static import calcul_masse_totale_passagers


from math import ceil
 
def fact(n):
    if n == 0 or n == 1:
        return 1
 
    else:
        return n * fact(n-1)
 

def pack_size(group_size, taille_groupe, height = True, classe = 'Y', WHCR = False):
    
    if classe == 'Y':
 
        L_values = []
        L_bound, S_bound = float('inf'), float('inf')
 
        for L in range(1,7):
 
            value = L + 2 * ceil(group_size / L)
 
            if value < L_bound:
 
                L_bound = value
                L_values = [L]
 
            elif value == L_bound:
 
                L_values.append(L)
 
        if len(L_values) == 1:
 
            L = L_values[0]
 
            return {'y': L, 'real_y': L + int(L > 3) + int(group_size == 3 and WHCR), 'x': ceil(group_size / L), 'air_bubbles': L*height - taille_groupe}
 
        else:
 
            if height:
 
                height_list = [ceil(group_size / L) for L in L_values]
                height = min(height_list)
                L = L_values[height_list.index(height)]
 
                return {'y': L, 'real_y': L + int(L > 3), 'x': height, 'air_bubbles': L*height - taille_groupe}
 
 
            else:    
 
                for L_value in L_values:
 
                    entropy = fact(L_value * ceil(group_size / L_value)) / (fact(L_value * ceil(group_size / L_value) - group_size) * fact(group_size))
 
                    if entropy < S_bound:
 
                        S_bound = entropy
                        L = L_value
 
            return {'y': L, 'real_y': L + int(L > 3), 'x': ceil(group_size / L), 'air_bubbles': L*ceil(group_size / L) - taille_groupe}        
        
    else:
        
        L_values = []
        L_bound, S_bound = float('inf'), float('inf')
 
        for L in range(1,5):
 
            value = L + 2 * ceil(group_size / L)
 
            if value < L_bound:
 
                L_bound = value
                L_values = [L]
 
            elif value == L_bound:
 
                L_values.append(L)
 
        if len(L_values) == 1:
 
            L = L_values[0]
 
            return {'y': L, 'real_y': 2*L - 1, 'x': ceil(group_size / L), 'air_bubbles': L*ceil(group_size / L) - taille_groupe}
 
        else:
 
            if height:
 
                height_list = [ceil(group_size / L) for L in L_values]
                height = min(height_list)
                L = L_values[height_list.index(height)]
 
                return {'y': L, 'real_y': 2*L - 1, 'x': height, 'air_bubbles': L*height - taille_groupe}
 
 
            else:    
 
                for L_value in L_values:
 
                    entropy = fact(L_value * ceil(group_size / L_value)) / (fact(L_value * ceil(group_size / L_value) - group_size) * fact(group_size))
 
                    if entropy < S_bound:
 
                        S_bound = entropy
                        L = L_value
 
            return {'y': L, 'real_y':2*L - 1, 'x': ceil(group_size / L), 'air_bubbles': L*ceil(group_size / L) - taille_groupe}





def intersect(l1,l2):
    aux = []
    for x in l1:
        if x in l2:
            aux.append(x)
    for x in l2:
        if x in l1:
            aux.append(x)  
    return list(set(aux))


def find_possible_paquets(PI_current, groupe_places, avion, listePassagers, listeGroupes, taille_groupe):
    '''
    Trouve tout les paquets sur toutes les lignes. Un paquet est défini par le plus petit ensemble de lignes qui contient tous les groupes à partir de la première ligne
    
    '''
    groupe_par_paquet = {x:{'groupes':[],'transit_time':[]} for x in range(1,(avion['x_max']+1))}
    
    for x in range(1,(avion['x_max']+1)):
        for y in range(1,avion['y_max']+1):
            for passager in listePassagers:
                if PI_current[x,y,passager.id_passager] == 1:
                    groupe_par_paquet[x]['groupes'].append(passager.idx)
                    if passager.transit_time not in groupe_par_paquet[x]['transit_time']:
                        groupe_par_paquet[x]['transit_time'].append(passager.transit_time)
                        
    paquets = {}
    time_packs = {}
    compteur = 0
    rows = []
    
    x = 1

    while x <= avion['x_max']:

        rows = [x]
        met_times = groupe_par_paquet[x]['transit_time']

        groupes_set = set(groupe_par_paquet[x]['groupes'])
        stack = [(groupe,0) for groupe in groupes_set]
        group_stack = [tup[0] for tup in stack]

        max_gap = 0

        while len(stack) > 0:

            groupe,rank = stack[0]

            x_gap = pack_size(listeGroupes[groupe].get_nombre_passagers(), taille_groupe)['x'] - 1

            if x_gap + rank > max_gap:
                max_gap = x_gap + rank

            new_groupes = []
            new_groupes_stack = []

            for k in range(rank + 1,x_gap + 1):

                met_times += groupe_par_paquet[x+k]['transit_time']
                new_groupes += [(new_groupe,k) for new_groupe in groupe_par_paquet[x]['groupes'] if new_groupe not in group_stack]
                new_groupes_stack += [new_groupe for new_groupe in groupe_par_paquet[x]['groupes'] if new_groupe not in group_stack]

            stack += list(set(new_groupes))
            group_stack += list(set(new_groupes_stack))
            stack = stack[1:]

        if len(set(met_times)) != 1 or len(intersect(groupe_places,group_stack)) > 0:

            x += max_gap + 1

        else:

            x += max_gap + 1
            x0 = rows[0]
            rows += [x0+k for k in range(1,max_gap+1)]
            paquets[compteur] = {'rangees': rows, 'transit_time': met_times[0]}
            compteur += 1
            
    return paquets   



def permutation_paquets(PI,groupe,groupe_places, avion, listePassagers, listeGroupes, taille_groupe, limit_return):
    '''
    Fonction qui échange les paquets entre eux.
    Permutation dite 'inter paquet'
    '''
    
    compteur_sol = 0
    coord_groupe_bf = []
    possible_paquets =  find_possible_paquets(PI, groupe_places, avion, listePassagers, listeGroupes, taille_groupe)

    liste_coord=[]
    for a,b in avion['seats']['real']:
        for p in listeGroupes[groupe].list_passagers:
            if PI[a,b,p.id_passager] == 1:
                liste_coord.append((a,b,p.id_passager))
    switch_feasible_paquets = [(PI,liste_coord)]
    #switch_feasible_paquets = []
    
    for i in range(len(list(possible_paquets.keys()))):
        
        tt_i = possible_paquets[i]['transit_time']
        len_i = len(possible_paquets[i]['rangees'])
        # vérification qu'on regarde bien le paquet associé au groupe
        bon_paquet = False
        for x in possible_paquets[i]['rangees']:
            for y in range(avion['y_max']+2):
                for p in listePassagers: 
                    if PI[x,y,p.id_passager] == 1 and p.idx==groupe:
                        bon_paquet = True         
        if bon_paquet:
            for j in range(len(list(possible_paquets.keys()))):
                PI_current = {(x,y,p): PI[x,y,p] for x,y,p in PI.keys()}
                if i!=j:
                    
                    tt_j  = possible_paquets[j]['transit_time']
                    len_j = len(possible_paquets[j]['rangees'])
                    
                    if tt_i==tt_j and len_i==len_j:
                        # échanger les paquets i et j, si c'est faisable bien sûr
                        
                        coord1 = []
                        coord2 = []
                        
                        for x in possible_paquets[i]['rangees']:
                            for y in range(avion['y_max']+2):
                                existe_passager1 = False
                                for p in listePassagers: # on peut chercher que dans les groupes sinon
                                    if PI[x,y,p.id_passager]==1:
                                        coord1.append((x,y,p))
                                        existe_passager1 = True
                                if not existe_passager1 :
                                    coord1.append((x,y,-1))
                                    
                        for x in possible_paquets[j]['rangees']:
                            for y in range(avion['y_max']+2):
                                existe_passager2 = False
                                for p in listePassagers:
                                    if PI[x,y,p.id_passager]==1:
                                        coord2.append((x,y,p))
                                        existe_passager2 = True
                                if not existe_passager2 :
                                    coord2.append((x,y,-1))

                        coord_groupe_new = []
                        
                        for k in range(len(coord1)):
                            
                            x1 = coord1[k][0]
                            y1 = coord1[k][1]
                            p1 = coord1[k][2]
                            
                            x2 = coord2[k][0]
                            y2 = coord2[k][1]
                            p2 = coord2[k][2]
                            
                            if type(p1)==type(-1) and type(p2)!=type(-1):
                                
                                PI_current[x1,y1,p2.id_passager]=1
                                
                                for p3 in listePassagers:
                                    
                                    PI_current[x2,y2,p3.id_passager]=0
                                    
                            elif type(p2)==type(-1) and type(p1)!=type(-1):
                                
                                PI_current[x2,y2,p1.id_passager]=1
                                
                                for p3 in listePassagers:
                                    
                                    PI_current[x1,y1,p3.id_passager]=0
                                    
                            elif type(p1)!=type(-1) and type(p2)!=type(-1):
                                
                                PI_current[x1,y1,p1.id_passager]=0
                                PI_current[x2,y2,p1.id_passager]=1
                                PI_current[x2,y2,p2.id_passager]=0
                                PI_current[x1,y1,p2.id_passager]=1

                            if type(p1)!=type(-1):
                                if p1.idx == groupe:
                                    coord_groupe_new.append((x2,y2,p1))
                                    coord_groupe_bf.append((x1,y1,p1))
                                    
                        # Maintenant on regarde si cette commutation est faisable
                        if feasible(PI_current, avion, listePassagers, listeGroupes) and compteur_sol<=limit_return:
                            switch_feasible_paquets.append((PI_current,coord_groupe_new))#ne pas faire attention aux p de coord2
                            compteur_sol+=1
    
    #switch_feasible_paquets.append((PI_current,coord_groupe_bf))
    return switch_feasible_paquets
 







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
        # print("cas 1")
        return False

    # sièges fictifs
    delta_fictif = sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['fictive'] for passager in listePassagers)

    if delta_fictif!=0:
        # print("cas 2")
        return False

    # au plus un passager par siège

    for x,y in avion['seats']['real']:
        if sum(PI[x,y,passager.id_passager] for passager in listePassagers) > 1:
            # print("cas 3")
            return False

    # exactement un siège par passager

    for passager in listePassagers:
        if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['real']) != 1:
            # print("cas 4")
            return False

    # pas d'enfant au niveau des issues de secours

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['exit'] for passager in listePassagers if passager.categorie == "enfants") != 0:
        # print("cas 5")
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
                                        # print("cas 6")
                                        return False
                            else:
                                if sum(PI[x, y+i, adulte.id_passager] for i in voisinage for adulte in listeGroupes[groupe].list_passagers if adulte.categorie != 'enfants') < PI[x, y, e]:
                                    # print("cas 7")
                                    return False

    # pas de passager Business en classe économique

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['eco'] for passager in listePassagers if passager.classe == "J") != 0 :
        # print("cas 8")
        return False

    # pas de passager économique en classe Business

    if sum(PI[x,y,passager.id_passager] for x,y in avion['seats']['business'] for passager in listePassagers if passager.classe == "Y") != 0 :
        # print("cas 9")
        return False

    # contraintes sur les wheelchaires

    val_interdites_y = [1,3,5,7]

    if sum(PI[x,y,w.id_passager] for x,y in avion['seats']['real'] for w in listePassagers if w.categorie == 'WHCR' and y in val_interdites_y) != 0 :
        # print("cas 10")
        return False

    for x,y in avion['seats']['real']:
        if y in [2,6]:
            for passager in listePassagers:
                if passager.categorie == 'WHCR':
                    if sum((y == 2) * (PI[x,y+1,p.id_passager] + PI[x-1,y+1,p.id_passager]) + (y == 6) * (PI[x,y-1,p.id_passager] + PI[x-1,y-1,p.id_passager]) + PI[x-1,y,p.id_passager] for p in listePassagers if p.id_passager != passager.id_passager) > 3 * (1 - PI[x,y,passager.id_passager]):
                        # print("cas 11")
                        return False

    # contraintes pour les x_max,x_min etc

    return True


###

def find_possible_switches(groupe, PI, groupe_places, avion, listePassagers, listeGroupes, limit_return): # Calcule toutes les configurations dans lesquelles le groupe 'groupe' peut être échangé avec un autre groupe
    '''
    Calcule toutes les configurations dans lesquelles le groupe 'groupe' peut être échangé avec un autre groupe
    Permutation dite 'inter-groupe'
    
    '''

    compteur_sol=0
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

                # Maintenant on regarde si cette commutation est faisable
                if feasible(PI_current, avion, listePassagers, listeGroupes) and compteur_sol<=limit_return:
                    switch_feasible.append((PI_current,coord2))
                    compteur_sol+=1
    
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

def find_possible_switches_passager(passager, PI, passager_places, avion, listePassagers, listeGroupes, limit_return): # Calcule toutes les configurations dans lesquelles le groupe 'groupe' peut être échangé avec un autre groupe
    '''
    Fonction qui détermine toutes les permutations dans un groupe.
    Permutation dite 'intra groupe'
    
    '''

    groupe = passager.idx
    compteur_sol = 0

    switch_feasible = []

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
                if feasible(PI_current, avion, listePassagers, listeGroupes) and compteur_sol<=limit_return:
                    switch_feasible.append((PI_current,coord2))
                    compteur_sol+=1

    return switch_feasible #contient la configuration de la commutation et la liste des nouvelles coordonnées du groupe


