"""
Script pour générer des données d'exemple pour tester les outils d'analyse.
Ce script crée des shapefiles et CSV fictifs représentant un réseau électrique
et des bâtiments dans une petite ville.
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_example_data(output_path: str = "data", num_buildings: int = 50):
    """
    Génère des données d'exemple pour tester les scripts d'analyse.
    
    Args:
        output_path: Chemin où sauvegarder les données
        num_buildings: Nombre de bâtiments à générer
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Génération de {num_buildings} bâtiments d'exemple...")
    
    # Définir une zone géographique (coordonnées fictives)
    np.random.seed(42)
    
    # Générer des postes de transformation
    logger.info("Génération des postes de transformation...")
    substations_data = {
        'substation_id': [1, 2, 3],
        'name': ['Poste Nord', 'Poste Centre', 'Poste Sud'],
        'capacity': [5000, 8000, 6000],
        'geometry': [
            Point(100, 200),
            Point(150, 150),
            Point(120, 80)
        ]
    }
    substations_gdf = gpd.GeoDataFrame(substations_data, crs='EPSG:3857')
    
    # Sauvegarder les postes
    substations_gdf.to_file(output_dir / 'substations.shp')
    logger.info(f"✓ {len(substations_gdf)} postes générés")
    
    # Générer un réseau électrique
    logger.info("Génération du réseau électrique...")
    network_segments = []
    segment_id = 1
    
    # Créer un réseau en étoile depuis chaque poste
    for idx, row in substations_gdf.iterrows():
        center = row.geometry
        
        # Lignes principales depuis le poste
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            angle_rad = np.radians(angle)
            length = np.random.uniform(30, 60)
            
            end_x = center.x + length * np.cos(angle_rad)
            end_y = center.y + length * np.sin(angle_rad)
            
            line = LineString([
                (center.x, center.y),
                (end_x, end_y)
            ])
            
            status = 'active' if np.random.random() > 0.2 else 'damaged'
            
            network_segments.append({
                'segment_id': segment_id,
                'status': status,
                'capacity': np.random.randint(100, 500),
                'geometry': line
            })
            segment_id += 1
            
            # Ajouter des segments secondaires
            if np.random.random() > 0.5:
                for sub_angle in [-30, 30]:
                    sub_angle_rad = angle_rad + np.radians(sub_angle)
                    sub_length = np.random.uniform(15, 30)
                    
                    sub_end_x = end_x + sub_length * np.cos(sub_angle_rad)
                    sub_end_y = end_y + sub_length * np.sin(sub_angle_rad)
                    
                    sub_line = LineString([
                        (end_x, end_y),
                        (sub_end_x, sub_end_y)
                    ])
                    
                    network_segments.append({
                        'segment_id': segment_id,
                        'status': 'active' if np.random.random() > 0.1 else 'damaged',
                        'capacity': np.random.randint(50, 200),
                        'geometry': sub_line
                    })
                    segment_id += 1
    
    network_gdf = gpd.GeoDataFrame(network_segments, crs='EPSG:3857')
    network_gdf.to_file(output_dir / 'network.shp')
    logger.info(f"✓ {len(network_gdf)} segments de réseau générés")
    
    # Générer des bâtiments
    logger.info("Génération des bâtiments...")
    buildings_data = []
    building_types = ['residential', 'residential', 'residential', 'residential', 
                     'commercial', 'school', 'hospital', 'residential']
    priorities = ['high', 'high', 'medium', 'medium', 'low']
    
    for i in range(num_buildings):
        # Position aléatoire dans la zone
        x = np.random.uniform(70, 180)
        y = np.random.uniform(50, 230)
        
        building_type = np.random.choice(building_types)
        
        # Nombre d'habitants dépend du type
        if building_type == 'residential':
            inhabitants = np.random.randint(1, 100)
        elif building_type == 'commercial':
            inhabitants = np.random.randint(5, 50)
        elif building_type == 'school':
            inhabitants = np.random.randint(100, 500)
        elif building_type == 'hospital':
            inhabitants = np.random.randint(50, 300)
        else:
            inhabitants = np.random.randint(1, 50)
        
        # Priorité dépend du type
        if building_type in ['hospital', 'school']:
            priority = 'high'
        elif building_type == 'commercial':
            priority = 'medium'
        else:
            priority = np.random.choice(priorities)
        
        # Statut de connexion (70% déconnectés)
        connected = np.random.random() > 0.7
        
        buildings_data.append({
            'building_id': i + 1,
            'inhabitants': inhabitants,
            'building_type': building_type,
            'connected': connected,
            'priority': priority,
            'geometry': Point(x, y)
        })
    
    buildings_gdf = gpd.GeoDataFrame(buildings_data, crs='EPSG:3857')
    buildings_gdf.to_file(output_dir / 'buildings.shp')
    logger.info(f"✓ {len(buildings_gdf)} bâtiments générés")
    
    # Générer le CSV des bâtiments
    logger.info("Génération du CSV des bâtiments...")
    buildings_csv_data = buildings_gdf.drop(columns=['geometry']).copy()
    buildings_csv_data.to_csv(output_dir / 'buildings.csv', index=False)
    logger.info(f"✓ CSV des bâtiments généré")
    
    # Générer le CSV des coûts
    logger.info("Génération du CSV des coûts...")
    costs_data = []
    
    for idx, building in buildings_gdf.iterrows():
        building_point = building.geometry
        
        # Trouver le segment de réseau le plus proche
        min_distance = float('inf')
        for _, segment in network_gdf.iterrows():
            distance = building_point.distance(segment.geometry)
            if distance < min_distance:
                min_distance = distance
        
        # Calculer le coût (basé sur la distance)
        base_cost = 100  # Coût de base
        distance_cost = min_distance * 50  # Coût par unité de distance
        
        # Majoration pour les bâtiments importants
        if building['building_type'] in ['hospital', 'school']:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        total_cost = (base_cost + distance_cost) * multiplier
        
        costs_data.append({
            'building_id': building['building_id'],
            'cost': round(total_cost, 2),
            'distance': round(min_distance, 2)
        })
    
    costs_df = pd.DataFrame(costs_data)
    costs_df.to_csv(output_dir / 'costs.csv', index=False)
    logger.info(f"✓ CSV des coûts généré")
    
    # Générer un fichier README
    readme_content = f"""# Données d'Exemple

Ces données ont été générées automatiquement pour tester les scripts d'analyse.

## Contenu

- **buildings.shp**: {len(buildings_gdf)} bâtiments
- **network.shp**: {len(network_gdf)} segments de réseau électrique
- **substations.shp**: {len(substations_gdf)} postes de transformation
- **buildings.csv**: Données tabulaires des bâtiments
- **costs.csv**: Coûts de raccordement estimés

## Statistiques

### Bâtiments
- Total: {len(buildings_gdf)}
- Connectés: {buildings_gdf['connected'].sum()}
- Déconnectés: {(~buildings_gdf['connected']).sum()}
- Population totale: {buildings_gdf['inhabitants'].sum()}

### Types de bâtiments
{buildings_gdf['building_type'].value_counts().to_string()}

### Priorités
{buildings_gdf['priority'].value_counts().to_string()}

### Réseau
- Segments: {len(network_gdf)}
- Segments actifs: {(network_gdf['status'] == 'active').sum()}
- Segments endommagés: {(network_gdf['status'] == 'damaged').sum()}
- Longueur totale: {network_gdf.geometry.length.sum():.2f} unités

## Utilisation

Pour analyser ces données, exécutez:

```bash
python scripts/main.py --data-path {output_path}
```
"""
    
    with open(output_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    logger.info("\n" + "="*60)
    logger.info("DONNÉES D'EXEMPLE GÉNÉRÉES AVEC SUCCÈS")
    logger.info(f"Emplacement: {output_dir.absolute()}")
    logger.info("="*60)
    logger.info("\nPour analyser ces données, exécutez:")
    logger.info(f"  python scripts/main.py --data-path {output_path}")


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Génère des données d'exemple pour tester les scripts d'analyse"
    )
    
    parser.add_argument(
        '--output-path',
        type=str,
        default='data',
        help='Chemin où sauvegarder les données (défaut: data)'
    )
    
    parser.add_argument(
        '--num-buildings',
        type=int,
        default=50,
        help='Nombre de bâtiments à générer (défaut: 50)'
    )
    
    args = parser.parse_args()
    
    generate_example_data(args.output_path, args.num_buildings)


if __name__ == "__main__":
    main()
