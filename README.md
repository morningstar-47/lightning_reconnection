# Lightning Reconnection

Planification du raccordement électrique de bâtiments après intempéries.

## Description

Ce projet vise à élaborer une planification optimisée pour le raccordement électrique de bâtiments dans une petite ville touchée par des intempéries. L'objectif principal est de rétablir rapidement la connexion électrique pour le plus grand nombre d'habitants, tout en minimisant les coûts.

## Fonctionnalités

- **Analyse de shapefiles** : Chargement et analyse de données géospatiales (bâtiments, réseau électrique, postes de transformation)
- **Analyse de CSV** : Traitement de données tabulaires (population, coûts, priorités)
- **Modélisation en graphe** : Représentation du réseau électrique comme un graphe avec NetworkX
- **Métriques de priorisation** : Algorithmes multi-critères pour optimiser l'ordre de raccordement
- **Visualisation** : Génération de graphiques et rapports

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/morningstar-47/lightning_reconnection.git
cd lightning_reconnection
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation Rapide

### Générer des données d'exemple

Pour tester le système avec des données fictives :

```bash
python examples/generate_example_data.py --output-path data --num-buildings 50
```

### Exécuter l'analyse complète

```bash
python scripts/main.py --data-path data --output-path output
```

Les résultats seront disponibles dans le répertoire `output/`.

## Structure du Projet

```
lightning_reconnection/
├── scripts/                    # Scripts d'analyse
│   ├── analyze_shapefiles.py  # Analyse de shapefiles
│   ├── analyze_csv.py          # Analyse de CSV
│   ├── network_model.py        # Modélisation en graphe
│   ├── prioritization.py       # Métriques de priorisation
│   ├── main.py                 # Script principal
│   └── README.md               # Documentation des scripts
├── examples/                   # Exemples et utilitaires
│   └── generate_example_data.py # Générateur de données
├── data/                       # Données d'entrée (à créer)
├── output/                     # Résultats (générés)
├── tests/                      # Tests unitaires
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

## Format des Données

### Shapefiles Requis

- `buildings.shp` : Points représentant les bâtiments
- `network.shp` : Lignes représentant le réseau électrique
- `substations.shp` : Points représentant les postes de transformation

### CSV Requis

- `buildings.csv` : Données des bâtiments (ID, habitants, type, etc.)
- `costs.csv` : Coûts de raccordement par bâtiment

Voir `scripts/README.md` pour plus de détails sur les formats attendus.

## Critères de Priorisation

Le système utilise une approche multi-critères avec les poids par défaut suivants :

- **Population** (40%) : Nombre d'habitants à reconnecter
- **Coût** (30%) : Coût du raccordement (inversé)
- **Urgence** (20%) : Priorité et type de bâtiment (hôpital, école)
- **Distance** (10%) : Distance au réseau existant (inversée)

Ces poids peuvent être ajustés selon vos besoins.

## Sorties Générées

- `network_graph.gexf` : Graphe du réseau (format Gephi)
- `network_visualization.png` : Visualisation du réseau
- `prioritized_buildings.csv` : Liste priorisée des bâtiments
- `prioritization_report.json` : Rapport détaillé
- `analysis_report.json` : Rapport complet
- `summary.txt` : Résumé textuel

## Utilisation Programmatique

Vous pouvez utiliser les modules individuellement dans votre code Python :

```python
from scripts.analyze_shapefiles import ShapefileAnalyzer
from scripts.network_model import NetworkGraphModel
from scripts.prioritization import PrioritizationMetric

# Analyser les shapefiles
analyzer = ShapefileAnalyzer('data')
buildings = analyzer.load_buildings('buildings.shp')
network = analyzer.load_network('network.shp')

# Créer un modèle de graphe
model = NetworkGraphModel()
graph = model.build_graph_from_geodataframes(network, buildings)

# Calculer les priorités
metric = PrioritizationMetric(population_weight=0.5)
prioritized = metric.prioritize_buildings(buildings_df)
```

## Tests

Pour exécuter les tests :

```bash
pytest tests/
```

## Documentation

Pour plus de détails, consultez :
- `scripts/README.md` : Documentation détaillée des scripts
- `examples/` : Exemples d'utilisation

## Licence

Voir le fichier `LICENSE` pour plus d'informations.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## Auteurs

Projet développé pour la planification de raccordement électrique après intempéries.
