# Lightning Reconnection

Planification optimisée du rétablissement du raccordement électrique des bâtiments d'une petite ville après intempéries. L'objectif est de maximiser le nombre d'habitants reconnectés dans les meilleurs délais tout en maîtrisant les coûts et les contraintes opérationnelles.

## Objectifs
- Rétablir rapidement l'alimentation électrique pour le plus grand nombre de foyers.
- Minimiser le coût total de raccordement dans le respect des contraintes techniques.
- Prioriser les interventions selon l'impact social et la faisabilité.

## Données et documents manquants (à fournir/valider)
Merci de compléter/valider les éléments ci-dessous pour fiabiliser la planification :

1) Type de chaque bâtiment
- Catégories proposées : habitation individuelle, immeuble collectif, établissement public, commerce, infrastructure critique, autre.
- Format attendu : identifiant_bâtiment → type_bâtiment.

2) Vérification du nombre de logements par bâtiment
- Confirmer le nombre de maisons/logements par bâtiment (ex. `nb_logements`).
- Indiquer la source (cadastre, syndic, relevé terrain) et la date de mise à jour.

3) Type de branchement par tronçon
- Indiquer si le raccordement est souterrain ou aérien (poteaux).
- Possibilité de mixte par tronçon ; préciser la proportion si applicable.

4) Coût unitaire de branchement (par mètre)
- Coût au mètre pour souterrain.
- Coût au mètre pour aérien (poteaux).
- Inclure, si possible, coûts fixes (mise en sécurité, ouverture/fermeture de chantier).

5) Durée unitaire d'intervention (par mètre)
- Durée au mètre pour souterrain.
- Durée au mètre pour aérien.
- Délais fixes (mobilisation équipe, accès site) si applicables.

## Paramètres du modèle (placeholders)
- `cout_par_metre_souterrain` : number (EUR/m).
- `cout_par_metre_aerien` : number (EUR/m).
- `duree_par_metre_souterrain` : number (min/m ou h/m).
- `duree_par_metre_aerien` : number (min/m ou h/m).
- `poids_priorite` : barème d'importance (ex. infrastructures critiques > collectifs > individuels).

## Méthodologie de planification (aperçu)
1. Consolidation des données (topologie réseau, types de bâtiments, métriques coût/temps).
2. Calcul des distances/longueurs par tronçon et typologie (SIG ou métrique fournie).
3. Estimation coûts/durées par scénario (souterrain/aérien/mixte).
4. Optimisation multi-critères (coût, temps, population reconnectée, contraintes).
5. Production d'un ordonnancement des interventions et d'estimations budgétaires.

## Hypothèses et contraintes
- Accès aux sites possible selon calendrier d'exploitation et autorisations.
- Conditions météo compatibles avec l'intervention.
- Ressources (équipes, matériel) limitées et planifiées par créneau.
- Priorités validées par la mairie et le gestionnaire de réseau.

## Livrables attendus
- Plan d'intervention ordonné (Gantt simplifié ou liste priorisée).
- Estimation du coût total et du coût par phase.
- Estimation des durées par phase et date de rétablissement progressive.
- Cartographie des tronçons avec typologie (souterrain/aérien) et métriques clés.

## Données d'entrée attendues (format minimal)
- `batiments.csv` : id_batiment, type_batiment, nb_logements, coord_x, coord_y, priorité.
- `troncons.csv` : id_troncon, id_depart, id_arrivee, longueur_m, type_branchement.
- `parametres.yaml` : coûts/durées unitaires, ressources, règles de priorité.

## Qualité et validation des données (checklist)
- Cohérence des types de bâtiments et des priorités.
- Vérification du nombre de logements par bâtiment (source + date).
- Typologie des branchements complète (aucune valeur manquante).
- Longueurs et coordonnées plausibles (contrôle des outliers).

## Collaborateurs
| Nom | Contact |
| --- | --- |
| OUAZAR Djamel | https://github.com/legb78 |
| Mopeno-BIa Emmanuel | https://github.com/morningstar-47 |
| HAMOUMA Amine | https://github.com/HamoumaAmine |
| ELMORTADA Hamza | https://github.com/weldhammadi |
