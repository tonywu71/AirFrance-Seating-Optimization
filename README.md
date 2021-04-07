# Projet AirFrance - Placement de Passagers
Groupe 2 - Thomas Bouquet, Caio De Prospero Iglesias, Quentin Guilhot, Thomas Melkior, Tony Wu

[TOC]

![image_presentation](assets/image_presentation.png)



## Partie 1

### Objectif

- Le projet vise à résoudre un problème d'optimisation visant à placer des passagers dans un avion de ligne de telle sorte à maximiser la satisfaction client tout en respectant un lot de consignes de sécurité obligatoires

- Un second objectif est bien évidemment de résoudre le problème en un temps minimum



Nous utiliserons pour cela le module *gurobi*.
​
​

### Présentation

Pour ce problème, on considère principalement un avion <strong>Airbus A320</strong> de la compagnie <strong>Air France</strong> dont l'organisation intérieure est présentée sur l'image suivante :

<br>
<img src='cabineA320AF.jpg'>
<br>
Il y a donc <strong>28 rangées</strong>, chacune possédant entre 2 et 6 sièges. Les dix premières rangées sont réservées à la classe Business (bien qu'on ne considère pas cette dernière dans la première instance de notre solution). Les issues de secours sont quant à elles situées aux rangées 11 et 12 (aucun enfant ne devra donc être assis sur un siège de l'une de ces deux rangées; mais encore une fois, cette contrainte ne s'appliquera pour les deuxième et troisième instances).



Toutefois, pour le vol du 8 novembre, un Airbus A320 est trop petit pour accueillir les 174 passagers. Pour cette date, on utilisera donc un <strong>Airbus A321</strong> dont le plan est présenté ci-dessous :
<br>
<img src='cabineA321AF.jpg'>
<br>

La cabine de cet avion est un peu plus complexe et est composé de <strong>34 rangées</strong> pour un total de 200 sièges.



### Webapp pour visualiser les résultats

Nous avons également implémenté une Web Application avec *Dash* pour permettre de visualiser aisément les résultats obtenus.

Pour l'utiliser, il faut :

> - Se mettre dans le répertoire `AirFrance-ST7`
> - Lancer `app_static.py` avec par exemple dans le terminal en lançant `python app_static.py`
> - Ouvrir dans un navigateur le lien affiché dans le terminal (commençant par *localhost*)



![preview_webapp](assets/statique_screen_preview.png)



### Evaluation des performances de l'algorithme proposé

- Pour le critère de certificat d'optimalité, les résultats pour chaque instance sont automatiquement enregistrées dans le dossier `output`
- Pour le critère de rapidité, les temps de calcul sont stockées dans le dossier `logs` dans des fichiers texte nommés avec le timestamp du moment où le calcul a été réalisé.



Les temps de calcul obtenus lors de nos essais tournent autour de 2 secondes pour les petites instances et autour de 2 minutes pour les plus difficiles (sur nos ordinateurs portables).





## Partie 2

### Objectif

### Présentation

### WebApp

#### Démonstration

![tuoriel_webapp](assets/tuoriel_webapp.gif)



#### Placement des passagers

![dynamique_screen_1](assets/dynamique_screen_1.png)

#### Visualisation de l'instance en cours de complétion

![dynamique_screen_2](assets/dynamique_screen_2.png)



Pour utiliser le WebApp, il faut :

> - Lancer au préalable `livrable_2.ipynb` avec la date et l'avion voulus pour générer la solution dans le dossier `output` (automatiquement généré après avoir lancer toutes les cellules)
> - Se mettre dans le répertoire `AirFrance-ST7`
> - Lancer `app_dynamic.py` **en donnant en argument la date et l'avion** par exemple dans le terminal en lançant la commande `python app_dynamic 17Nov A321.py`
> - Ouvrir dans un navigateur le lien affiché dans le terminal (commençant par *localhost*)
> - On arrive sur l'interface sur l'onglet *Sélection des places*
> - Pour le passager indiqué par les deux sliders, sélectionner la place proposée en cliquant sur le point correspondant
> - Cliquer sur valider et si affichage de l'animation de chargement, attendre qu'il disparaisse (indique la fin des calculs)
> - Continuer ainsi de suite jusqu'à remplissage de l'avion
> - Pendant le remplissage, il est possible d'aller dans l'onglet *Prévisualisation* pour observer les placements de passager déjà réalisés.



### Evaluation des performances de l'algorithme proposé



## Notes de version :

- v2.0
  - Release du 3ème rendu avec la partie dynamique
  - **Cahier des charges pour la 2ème partie :**
    - Offrir un maximum de choix de sièges
    - Atteinte des objectifs de base
    - Satisfaction client
    - Centrage de l’avion
    - Placement à l’avant des passagers en correspondance
    - Respect des contraintes supplémentaires
    - Placement spécial des passagers enfants, et des passagers à
      mobilité réduire
    - Ajout d’une cabine business

- v1.1
  - Ajout des images manquantes dans le Dash
- 1.0
  - Release du 2ème rendu avec la partie statique
  - **Cahier des charges pour la 2ème partie :**
    - Pas de choix de siège
    - Atteinte des objectifs de base
    - Satisfaction client
    - Centrage de l’avion
    - Placement à l’avant des passagers en correspondance
    - Respect des contraintes supplémentaires
    - Placement spécial des passagers enfants, et des passagers à mobilité réduire
    - Ajout d’une cabine business