# Résumé du Projet - Planification du Raccordement Électrique

## Vue d'Ensemble

Ce projet fournit une solution complète pour la planification optimisée du raccordement électrique de bâtiments après des intempéries. Il utilise une approche multi-critères pour prioriser les raccordements afin de reconnecter rapidement le maximum d'habitants tout en minimisant les coûts.

## Fonctionnalités Implémentées

### 1. Analyse de Shapefiles (`scripts/analyze_shapefiles.py`)

**Capacités:**
- Chargement de données géospatiales (bâtiments, réseau, postes)
- Calcul de statistiques spatiales
- Jointures spatiales entre bâtiments et réseau
- Identification des connexions les plus proches

**Classes principales:**
- `ShapefileAnalyzer`: Analyseur principal pour données géospatiales

**Méthodes clés:**
- `load_buildings()`: Charge les bâtiments
- `load_network()`: Charge le réseau électrique
- `calculate_building_stats()`: Statistiques des bâtiments
- `spatial_join_buildings_network()`: Jointure spatiale

### 2. Analyse de CSV (`scripts/analyze_csv.py`)

**Capacités:**
- Chargement et traitement de données tabulaires
- Fusion de multiples sources de données
- Identification des bâtiments prioritaires
- Calcul d'efficacité coût/habitants

**Classes principales:**
- `CSVAnalyzer`: Analyseur pour données CSV

**Méthodes clés:**
- `load_buildings_data()`: Charge les données des bâtiments
- `analyze_buildings()`: Analyse complète des bâtiments
- `identify_priority_buildings()`: Identifie les priorités
- `calculate_cost_efficiency()`: Calcule l'efficacité

### 3. Modélisation du Réseau en Graphe (`scripts/network_model.py`)

**Capacités:**
- Représentation du réseau comme un graphe NetworkX
- Calcul de chemins optimaux
- Identification de nœuds critiques
- Analyse de connectivité
- Visualisation du réseau

**Classes principales:**
- `NetworkGraphModel`: Modèle de graphe du réseau

**Méthodes clés:**
- `build_graph_from_geodataframes()`: Construit le graphe
- `find_shortest_path()`: Trouve le plus court chemin
- `calculate_network_statistics()`: Statistiques du réseau
- `identify_critical_nodes()`: Identifie les nœuds critiques

### 4. Métriques de Priorisation (`scripts/prioritization.py`)

**Capacités:**
- Système multi-critères configurable
- Normalisation des scores
- Calcul de scores composites
- Analyse d'impact cumulatif

**Classes principales:**
- `PrioritizationMetric`: Système de priorisation

**Critères de priorisation:**
1. **Population** (40%): Nombre d'habitants affectés
2. **Coût** (30%): Coût du raccordement (inversé)
3. **Urgence** (20%): Type de bâtiment et priorité explicite
4. **Distance** (10%): Distance au réseau (inversée)

**Méthodes clés:**
- `calculate_composite_score()`: Calcule le score final
- `prioritize_buildings()`: Trie les bâtiments par priorité
- `calculate_cumulative_impact()`: Impact cumulatif
- `generate_priority_report()`: Génère un rapport

### 5. Script Principal (`scripts/main.py`)

**Capacités:**
- Orchestration complète de toutes les analyses
- Pipeline automatisé
- Génération de rapports multiples
- Interface en ligne de commande

**Classes principales:**
- `ElectricalReconnectionPlanner`: Planificateur principal

**Workflow:**
1. Analyse des shapefiles
2. Analyse des CSV
3. Modélisation en graphe
4. Calcul des priorités
5. Génération des rapports

## Sorties Générées

### Fichiers de Sortie

1. **summary.txt**: Résumé textuel de l'analyse
   - Nombre de bâtiments et habitants
   - Statistiques du réseau
   - Top 20% des bâtiments prioritaires

2. **prioritized_buildings.csv**: Liste complète priorisée
   - Tous les scores individuels
   - Score composite
   - Rang de priorité
   - Métriques cumulatives

3. **network_visualization.png**: Visualisation du réseau
   - Réseau électrique
   - Bâtiments
   - Postes de transformation

4. **network_graph.gexf**: Graphe au format GEXF
   - Compatible avec Gephi
   - Analyse de réseau avancée

5. **prioritization_report.json**: Rapport détaillé
   - Top 10 des bâtiments
   - Statistiques sur tous les scores
   - Analyse des 20% les plus prioritaires

6. **analysis_report.json**: Rapport complet
   - Statistiques des shapefiles
   - Statistiques des CSV
   - Statistiques du graphe
   - Nœuds critiques

## Utilisation

### Installation

```bash
pip install -r requirements.txt
```

### Génération de Données d'Exemple

```bash
python examples/generate_example_data.py --output-path data --num-buildings 50
```

### Exécution de l'Analyse

```bash
python scripts/main.py --data-path data --output-path output
```

### Utilisation Programmatique

```python
from scripts.prioritization import PrioritizationMetric

# Créer un système de priorisation personnalisé
metric = PrioritizationMetric(
    population_weight=0.5,
    cost_weight=0.2,
    urgency_weight=0.2,
    distance_weight=0.1
)

# Prioriser les bâtiments
prioritized = metric.prioritize_buildings(buildings_df)
```

## Tests

### Couverture des Tests

- 14 tests unitaires
- Couverture de toutes les classes principales
- Tests d'intégration avec données synthétiques

### Exécution des Tests

```bash
pytest tests/test_analysis_scripts.py -v
```

**Résultat:** ✓ 14/14 tests passent

## Exemple de Résultats

Pour un réseau de 20 bâtiments avec 1991 habitants:

- **Top 20% des bâtiments** (4 bâtiments):
  - Couvrent 992 habitants (49.8% de la population)
  - Coût total: 1 296.59 unités monétaires
  - Comprennent principalement des écoles et bâtiments résidentiels à forte population

- **Réseau**:
  - 52 segments de réseau
  - 45 actifs, 7 endommagés
  - Longueur totale: 1 667.35 unités
  - 3 postes de transformation

- **Graphe**:
  - 78 nœuds (55 réseau, 3 postes, 20 bâtiments)
  - 75 arêtes
  - Réseau non entièrement connecté (multiple composantes)

## Architecture du Code

### Organisation des Modules

```
scripts/
├── analyze_shapefiles.py  # Analyse géospatiale
├── analyze_csv.py          # Analyse tabulaire
├── network_model.py        # Modélisation en graphe
├── prioritization.py       # Métriques de priorisation
└── main.py                 # Orchestration
```

### Dépendances Principales

- **geopandas**: Données géospatiales
- **networkx**: Analyse de graphes
- **pandas**: Manipulation de données
- **shapely**: Géométries
- **matplotlib**: Visualisation

### Points de Design

1. **Modularité**: Chaque script est indépendant et réutilisable
2. **Extensibilité**: Facile d'ajouter de nouveaux critères ou analyses
3. **Configuration**: Poids des critères ajustables
4. **Robustesse**: Gestion des erreurs et données manquantes
5. **Documentation**: Code bien documenté avec docstrings

## Cas d'Usage

### 1. Planification d'Urgence
Identifier rapidement les bâtiments prioritaires (hôpitaux, écoles) pour intervention immédiate.

### 2. Optimisation Budgétaire
Déterminer combien de bâtiments peuvent être reconnectés avec un budget limité.

### 3. Analyse d'Impact
Évaluer l'impact de différentes stratégies de raccordement sur la population.

### 4. Identification de Points Critiques
Trouver les segments de réseau critiques dont la réparation bénéficierait au plus grand nombre.

## Améliorations Futures Possibles

1. **Interface Web**: Dashboard interactif pour visualisation
2. **Optimisation Multi-objectifs**: Algorithmes génétiques ou programmation linéaire
3. **Prédiction de Durée**: Estimation du temps de reconnexion
4. **Analyse Temporelle**: Planification en phases
5. **Intégration SIG**: Export vers ArcGIS/QGIS
6. **API REST**: Service web pour intégration système

## Validation

- ✅ Tests unitaires: 14/14 passent
- ✅ Revue de code: Aucun problème détecté
- ✅ Analyse de sécurité (CodeQL): Aucune vulnérabilité
- ✅ Test d'intégration: Analyse complète réussie
- ✅ Génération de données d'exemple: Fonctionnelle
- ✅ Documentation: Complète (README, USAGE_GUIDE, docstrings)

## Performance

Sur un dataset de 50 bâtiments avec 52 segments de réseau:
- Temps d'exécution total: ~5 secondes
- Génération du graphe: <1 seconde
- Calcul des priorités: <1 seconde
- Visualisation: ~3 secondes

## Conclusion

Ce projet fournit une solution complète, testée et documentée pour la planification du raccordement électrique. Il utilise des technologies modernes (geopandas, networkx) et des algorithmes éprouvés (graphes, multi-critères) pour résoudre un problème réel d'optimisation post-catastrophe.

Le système est flexible, extensible et peut être adapté à différents contextes et priorités. La documentation complète et les exemples facilitent l'adoption et l'utilisation par différents profils d'utilisateurs (analystes, décideurs, développeurs).
