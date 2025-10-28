# Scripts pour l'Analyse et la Priorisation du Raccordement Électrique

Ce répertoire contient les scripts Python pour analyser les données géospatiales et CSV, modéliser le réseau électrique en graphe, et calculer les métriques de priorisation pour le raccordement des bâtiments.

## Structure des Scripts

### Scripts Principaux

1. **main.py** - Script principal orchestrant toute l'analyse
2. **analyze_shapefiles.py** - Analyse des fichiers shapefile (géométries)
3. **analyze_csv.py** - Analyse des fichiers CSV (données tabulaires)
4. **network_model.py** - Modélisation du réseau électrique en graphe
5. **prioritization.py** - Calcul des métriques de priorisation

## Installation

Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## Utilisation

### Utilisation Simple

Placez vos fichiers de données dans le répertoire `data/` et exécutez :

```bash
python scripts/main.py
```

Les résultats seront générés dans le répertoire `output/`.

### Utilisation Avancée

Vous pouvez spécifier des chemins personnalisés :

```bash
python scripts/main.py \
  --data-path /chemin/vers/donnees \
  --output-path /chemin/vers/sortie \
  --buildings-shp buildings.shp \
  --network-shp network.shp \
  --substations-shp substations.shp \
  --buildings-csv buildings.csv \
  --costs-csv costs.csv
```

### Utilisation Programmatique

#### Analyse des Shapefiles

```python
from analyze_shapefiles import ShapefileAnalyzer

analyzer = ShapefileAnalyzer('data')
buildings = analyzer.load_buildings('buildings.shp')
network = analyzer.load_network('network.shp')

# Statistiques
stats = analyzer.calculate_building_stats()
print(f"Nombre de bâtiments: {stats['count']}")
print(f"Population totale: {stats.get('total_inhabitants', 'N/A')}")
```

#### Analyse des CSV

```python
from analyze_csv import CSVAnalyzer

analyzer = CSVAnalyzer('data')
buildings_df = analyzer.load_buildings_data('buildings.csv')

# Analyse
analysis = analyzer.analyze_buildings()
print(f"Bâtiments déconnectés: {analysis.get('disconnected_count', 0)}")

# Identifier les bâtiments prioritaires
prioritized = analyzer.identify_priority_buildings()
```

#### Modélisation du Réseau

```python
from network_model import NetworkGraphModel

model = NetworkGraphModel()
graph = model.build_graph_from_geodataframes(
    network_gdf, buildings_gdf, substations_gdf
)

# Statistiques du graphe
stats = model.calculate_network_statistics()
print(f"Nœuds: {stats['nodes']}, Arêtes: {stats['edges']}")

# Trouver le chemin le plus court
path = model.find_shortest_path('building_1', 'substation_1')
cost = model.calculate_path_cost(path)

# Identifier les nœuds critiques
critical_nodes = model.identify_critical_nodes(top_n=10)
```

#### Priorisation

```python
from prioritization import PrioritizationMetric

# Créer le système de priorisation avec des poids personnalisés
metric = PrioritizationMetric(
    population_weight=0.4,  # 40% pour la population
    cost_weight=0.3,         # 30% pour le coût
    urgency_weight=0.2,      # 20% pour l'urgence
    distance_weight=0.1      # 10% pour la distance
)

# Calculer les priorités
prioritized_df = metric.prioritize_buildings(buildings_df)

# Top 10 des bâtiments prioritaires
top_10 = prioritized_df.head(10)
print(top_10[['building_id', 'composite_score', 'priority_rank']])

# Calculer l'impact cumulatif
cumulative_df = metric.calculate_cumulative_impact(prioritized_df)

# Générer un rapport
report = metric.generate_priority_report(cumulative_df, 'output/report.json')
```

## Format des Données Attendues

### Shapefiles

#### buildings.shp
- Géométrie: Point
- Attributs suggérés:
  - `building_id`: Identifiant unique
  - `inhabitants`: Nombre d'habitants
  - `building_type`: Type de bâtiment (residential, hospital, school, etc.)
  - `connected`: Statut de connexion (booléen)
  - `priority`: Priorité (high/medium/low)

#### network.shp
- Géométrie: LineString
- Attributs suggérés:
  - `segment_id`: Identifiant du segment
  - `status`: Statut (active/damaged)
  - `capacity`: Capacité
  - `length`: Longueur du segment

#### substations.shp
- Géométrie: Point
- Attributs suggérés:
  - `substation_id`: Identifiant
  - `name`: Nom du poste
  - `capacity`: Capacité

### Fichiers CSV

#### buildings.csv
```csv
building_id,inhabitants,building_type,connected,priority
1,25,residential,false,high
2,50,residential,false,medium
3,100,hospital,false,critical
```

#### costs.csv
```csv
building_id,cost,distance
1,5000,45
2,7500,60
3,3000,30
```

## Sorties Générées

Le script génère les fichiers suivants dans le répertoire `output/` :

1. **network_graph.gexf** - Graphe du réseau au format GEXF (visualisable avec Gephi)
2. **network_visualization.png** - Visualisation du graphe
3. **prioritized_buildings.csv** - Liste des bâtiments priorisés avec scores
4. **prioritization_report.json** - Rapport détaillé de priorisation
5. **analysis_report.json** - Rapport complet de l'analyse
6. **summary.txt** - Résumé textuel de l'analyse

## Critères de Priorisation

Le système utilise quatre critères principaux :

1. **Population** (40% par défaut) - Nombre d'habitants affectés
2. **Coût** (30% par défaut) - Coût du raccordement (inversé)
3. **Urgence** (20% par défaut) - Priorité explicite et type de bâtiment
4. **Distance** (10% par défaut) - Distance au réseau (inversée)

Le score composite final est calculé comme suit :
```
score_composite = 0.4 × score_population + 0.3 × score_coût + 0.2 × score_urgence + 0.1 × score_distance
```

Les poids peuvent être ajustés selon les priorités spécifiques du projet.

## Fonctionnalités Avancées

### Identification des Nœuds Critiques

Le système identifie les nœuds critiques du réseau en utilisant la centralité d'intermédiarité (betweenness centrality). Ces nœuds sont importants car leur défaillance peut isoler plusieurs bâtiments.

### Analyse d'Impact Cumulatif

Le système calcule l'impact cumulatif du raccordement en fonction de l'ordre de priorité, permettant de répondre à des questions comme :
- Combien d'habitants peuvent être reconnectés avec un budget de X euros ?
- Quel pourcentage de la population sera reconnecté après avoir traité les N premiers bâtiments ?

### Jointure Spatiale

Le système peut effectuer des jointures spatiales entre les bâtiments et le réseau pour identifier automatiquement quels bâtiments sont à proximité de quels segments du réseau.

## Dépannage

### Erreur "Fichier non trouvé"
Assurez-vous que vos fichiers de données sont dans le répertoire spécifié et que les noms correspondent exactement.

### Erreur "Aucune colonne trouvée"
Vérifiez que vos fichiers CSV/shapefiles contiennent les colonnes attendues. Le système est tolérant et fonctionnera avec des données partielles.

### Graphe non connecté
Si le réseau n'est pas connecté, cela peut indiquer :
- Des segments isolés dans le réseau
- Des postes de transformation non connectés
- Des erreurs de données

Utilisez la visualisation du graphe pour identifier les problèmes.

## Exemples

Voir le répertoire `examples/` pour des exemples de données et des notebooks Jupyter démontrant l'utilisation des scripts.
