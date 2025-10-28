# Guide d'Utilisation Rapide

Ce guide vous montre comment utiliser les scripts d'analyse pour la planification du raccordement électrique.

## Prérequis

1. Python 3.8 ou supérieur
2. Dépendances installées : `pip install -r requirements.txt`

## Scénario 1 : Utiliser des Données d'Exemple

### Étape 1 : Générer des Données d'Exemple

```bash
python examples/generate_example_data.py --output-path data --num-buildings 50
```

Cela crée :
- `data/buildings.shp` - 50 bâtiments fictifs
- `data/network.shp` - Réseau électrique fictif
- `data/substations.shp` - Postes de transformation
- `data/buildings.csv` - Données CSV des bâtiments
- `data/costs.csv` - Coûts de raccordement

### Étape 2 : Exécuter l'Analyse Complète

```bash
python scripts/main.py --data-path data --output-path output
```

### Étape 3 : Consulter les Résultats

Les résultats sont dans le répertoire `output/` :

1. **summary.txt** - Résumé lisible de l'analyse
2. **prioritized_buildings.csv** - Liste des bâtiments priorisés
3. **network_visualization.png** - Visualisation du réseau
4. **network_graph.gexf** - Graphe (ouvrir avec Gephi)
5. **prioritization_report.json** - Rapport détaillé
6. **analysis_report.json** - Analyse complète

## Scénario 2 : Utiliser Vos Propres Données

### Format des Shapefiles

Vos shapefiles doivent contenir :

**buildings.shp** (Points)
- `building_id` : Identifiant unique
- `inhabitants` : Nombre d'habitants
- `building_type` : Type (residential, hospital, school, commercial)
- `connected` : État de connexion (True/False)
- `priority` : Priorité (high/medium/low)

**network.shp** (Lignes)
- `segment_id` : Identifiant du segment
- `status` : État (active/damaged)
- `capacity` : Capacité (optionnel)

**substations.shp** (Points)
- `substation_id` : Identifiant
- `name` : Nom du poste
- `capacity` : Capacité

### Format des CSV

**buildings.csv**
```csv
building_id,inhabitants,building_type,connected,priority
1,50,residential,false,high
2,100,school,false,critical
3,25,commercial,true,low
```

**costs.csv**
```csv
building_id,cost,distance
1,5000,45.5
2,7500,60.2
3,3000,30.0
```

### Exécuter l'Analyse

```bash
python scripts/main.py \
  --data-path /chemin/vers/vos/donnees \
  --output-path /chemin/vers/resultats \
  --buildings-shp mes_batiments.shp \
  --network-shp mon_reseau.shp \
  --substations-shp mes_postes.shp \
  --buildings-csv mes_batiments.csv \
  --costs-csv mes_couts.csv
```

## Scénario 3 : Utilisation Programmatique

### Exemple : Analyse Personnalisée

```python
from scripts.analyze_csv import CSVAnalyzer
from scripts.prioritization import PrioritizationMetric

# Charger les données
analyzer = CSVAnalyzer('data')
buildings_df = analyzer.load_buildings_data('buildings.csv')
costs_df = analyzer.load_costs_data('costs.csv')

# Fusionner les données
merged_df = analyzer.merge_data(buildings_df, costs_df)

# Créer un système de priorisation personnalisé
# Donner plus de poids à la population et moins au coût
metric = PrioritizationMetric(
    population_weight=0.5,  # 50% pour la population
    cost_weight=0.2,        # 20% pour le coût
    urgency_weight=0.2,     # 20% pour l'urgence
    distance_weight=0.1     # 10% pour la distance
)

# Calculer les priorités
prioritized_df = metric.prioritize_buildings(merged_df)

# Afficher les 10 premiers
print("Top 10 des bâtiments prioritaires:")
print(prioritized_df[['building_id', 'inhabitants', 'cost', 'composite_score']].head(10))

# Calculer l'impact cumulatif
cumulative_df = metric.calculate_cumulative_impact(prioritized_df)

# Combien d'habitants reconnectés avec un budget de 10000 ?
budget = 10000
within_budget = cumulative_df[cumulative_df['cumulative_cost'] <= budget]
print(f"\nAvec un budget de {budget}:")
print(f"- Bâtiments reconnectés: {len(within_budget)}")
print(f"- Habitants reconnectés: {within_budget['cumulative_inhabitants'].iloc[-1]}")
```

### Exemple : Analyse du Réseau

```python
from scripts.analyze_shapefiles import ShapefileAnalyzer
from scripts.network_model import NetworkGraphModel

# Charger les shapefiles
analyzer = ShapefileAnalyzer('data')
buildings_gdf = analyzer.load_buildings('buildings.shp')
network_gdf = analyzer.load_network('network.shp')
substations_gdf = analyzer.load_substations('substations.shp')

# Créer le modèle de graphe
model = NetworkGraphModel()
graph = model.build_graph_from_geodataframes(
    network_gdf, buildings_gdf, substations_gdf
)

# Statistiques du graphe
stats = model.calculate_network_statistics()
print(f"Réseau connecté: {stats['is_connected']}")
print(f"Nombre de composantes: {stats['number_of_components']}")
print(f"Longueur totale du réseau: {stats['total_network_length']:.2f}")

# Identifier les nœuds critiques
critical_nodes = model.identify_critical_nodes(top_n=5)
print("\nTop 5 des nœuds critiques:")
for node, centrality in critical_nodes:
    print(f"  {node}: {centrality:.4f}")

# Trouver le chemin le plus court pour un bâtiment
building_node = 'building_0'
substation_node = 'substation_1'
path = model.find_shortest_path(building_node, substation_node)
cost = model.calculate_path_cost(path)
print(f"\nChemin de {building_node} à {substation_node}:")
print(f"  Distance: {cost:.2f}")
print(f"  Nombre de segments: {len(path) - 1}")
```

## Personnalisation des Critères de Priorisation

Vous pouvez ajuster les poids selon vos priorités :

```python
# Priorité maximale à la population
metric = PrioritizationMetric(
    population_weight=0.7,
    cost_weight=0.1,
    urgency_weight=0.15,
    distance_weight=0.05
)

# Priorité maximale au coût (économie)
metric = PrioritizationMetric(
    population_weight=0.2,
    cost_weight=0.5,
    urgency_weight=0.2,
    distance_weight=0.1
)

# Équilibré
metric = PrioritizationMetric(
    population_weight=0.25,
    cost_weight=0.25,
    urgency_weight=0.25,
    distance_weight=0.25
)
```

## Interprétation des Résultats

### Score Composite
- Entre 0 et 1
- Plus le score est élevé, plus le bâtiment est prioritaire
- Basé sur une combinaison pondérée des 4 critères

### Rang de Priorité
- 1 = le plus prioritaire
- Permet de trier facilement les bâtiments

### Impact Cumulatif
- `cumulative_inhabitants` : Nombre total d'habitants reconnectés jusqu'à cette ligne
- `cumulative_cost` : Coût total dépensé jusqu'à cette ligne
- Permet d'analyser l'efficacité de la stratégie de raccordement

## Dépannage

### Erreur : "No module named 'geopandas'"
```bash
pip install geopandas
```

### Erreur : "FileNotFoundError"
Vérifiez que vos fichiers sont dans le bon répertoire et que les noms correspondent.

### Graphe non connecté
C'est normal si votre réseau a des sections isolées. Consultez la visualisation pour identifier les composantes.

## Support

Pour plus d'informations :
- Consultez `scripts/README.md` pour la documentation détaillée
- Exécutez `python scripts/main.py --help` pour les options
- Examinez les tests dans `tests/` pour des exemples d'utilisation
