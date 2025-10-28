"""
Script pour l'analyse des shapefiles.
Ce script permet de charger, analyser et traiter des données géospatiales
à partir de fichiers shapefiles contenant des informations sur les bâtiments
et le réseau électrique.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShapefileAnalyzer:
    """Classe pour analyser les shapefiles du réseau électrique et des bâtiments."""
    
    def __init__(self, data_path: str = "data"):
        """
        Initialise l'analyseur de shapefiles.
        
        Args:
            data_path: Chemin vers le répertoire contenant les shapefiles
        """
        self.data_path = Path(data_path)
        self.buildings = None
        self.network = None
        self.substations = None
        
    def load_shapefile(self, filename: str, layer_name: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Charge un shapefile.
        
        Args:
            filename: Nom du fichier shapefile
            layer_name: Nom de la couche à charger (optionnel)
            
        Returns:
            GeoDataFrame contenant les données du shapefile
        """
        filepath = self.data_path / filename
        
        if not filepath.exists():
            logger.error(f"Le fichier {filepath} n'existe pas")
            raise FileNotFoundError(f"Le fichier {filepath} n'existe pas")
        
        try:
            if layer_name:
                gdf = gpd.read_file(filepath, layer=layer_name)
            else:
                gdf = gpd.read_file(filepath)
            
            logger.info(f"Shapefile chargé: {filename} ({len(gdf)} entités)")
            return gdf
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filename}: {str(e)}")
            raise
    
    def load_buildings(self, filename: str = "buildings.shp") -> gpd.GeoDataFrame:
        """
        Charge le shapefile des bâtiments.
        
        Args:
            filename: Nom du fichier shapefile des bâtiments
            
        Returns:
            GeoDataFrame des bâtiments
        """
        self.buildings = self.load_shapefile(filename)
        logger.info(f"Bâtiments chargés: {len(self.buildings)} bâtiments")
        return self.buildings
    
    def load_network(self, filename: str = "network.shp") -> gpd.GeoDataFrame:
        """
        Charge le shapefile du réseau électrique.
        
        Args:
            filename: Nom du fichier shapefile du réseau
            
        Returns:
            GeoDataFrame du réseau électrique
        """
        self.network = self.load_shapefile(filename)
        logger.info(f"Réseau chargé: {len(self.network)} segments")
        return self.network
    
    def load_substations(self, filename: str = "substations.shp") -> gpd.GeoDataFrame:
        """
        Charge le shapefile des postes de transformation.
        
        Args:
            filename: Nom du fichier shapefile des postes
            
        Returns:
            GeoDataFrame des postes de transformation
        """
        self.substations = self.load_shapefile(filename)
        logger.info(f"Postes chargés: {len(self.substations)} postes")
        return self.substations
    
    def get_basic_statistics(self, gdf: gpd.GeoDataFrame) -> Dict:
        """
        Calcule des statistiques de base sur un GeoDataFrame.
        
        Args:
            gdf: GeoDataFrame à analyser
            
        Returns:
            Dictionnaire contenant les statistiques
        """
        stats = {
            'count': len(gdf),
            'crs': str(gdf.crs),
            'bounds': gdf.total_bounds.tolist(),
            'geometry_types': gdf.geometry.geom_type.value_counts().to_dict(),
            'columns': gdf.columns.tolist()
        }
        
        # Ajouter des statistiques sur les colonnes numériques
        numeric_cols = gdf.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats['numeric_stats'] = gdf[numeric_cols].describe().to_dict()
        
        return stats
    
    def calculate_building_stats(self) -> Dict:
        """
        Calcule des statistiques sur les bâtiments.
        
        Returns:
            Dictionnaire contenant les statistiques des bâtiments
        """
        if self.buildings is None:
            raise ValueError("Les bâtiments n'ont pas été chargés")
        
        stats = self.get_basic_statistics(self.buildings)
        
        # Calculs spécifiques aux bâtiments
        if 'area' not in self.buildings.columns:
            stats['total_area'] = self.buildings.geometry.area.sum()
            stats['mean_area'] = self.buildings.geometry.area.mean()
        
        # Calculer le nombre d'habitants si la colonne existe
        if 'inhabitants' in self.buildings.columns or 'population' in self.buildings.columns:
            pop_col = 'inhabitants' if 'inhabitants' in self.buildings.columns else 'population'
            stats['total_inhabitants'] = int(self.buildings[pop_col].sum())
            stats['mean_inhabitants'] = float(self.buildings[pop_col].mean())
        
        return stats
    
    def calculate_network_stats(self) -> Dict:
        """
        Calcule des statistiques sur le réseau électrique.
        
        Returns:
            Dictionnaire contenant les statistiques du réseau
        """
        if self.network is None:
            raise ValueError("Le réseau n'a pas été chargé")
        
        stats = self.get_basic_statistics(self.network)
        
        # Calculs spécifiques au réseau
        stats['total_length'] = self.network.geometry.length.sum()
        stats['mean_length'] = self.network.geometry.length.mean()
        
        # Statut du réseau si disponible
        if 'status' in self.network.columns:
            stats['status_counts'] = self.network['status'].value_counts().to_dict()
        
        return stats
    
    def find_nearest_network_point(self, building_point: 'Point', max_distance: float = 100.0) -> Tuple[Optional[int], Optional[float]]:
        """
        Trouve le point du réseau le plus proche d'un bâtiment.
        
        Args:
            building_point: Point représentant le bâtiment
            max_distance: Distance maximale de recherche
            
        Returns:
            Tuple (index du segment, distance) ou (None, None) si rien trouvé
        """
        if self.network is None:
            raise ValueError("Le réseau n'a pas été chargé")
        
        distances = self.network.geometry.distance(building_point)
        min_idx = distances.idxmin()
        min_distance = distances[min_idx]
        
        if min_distance <= max_distance:
            return min_idx, min_distance
        return None, None
    
    def spatial_join_buildings_network(self, buffer_distance: float = 50.0) -> gpd.GeoDataFrame:
        """
        Effectue une jointure spatiale entre les bâtiments et le réseau.
        
        Args:
            buffer_distance: Distance du buffer autour du réseau
            
        Returns:
            GeoDataFrame avec les bâtiments associés au réseau
        """
        if self.buildings is None or self.network is None:
            raise ValueError("Les bâtiments et le réseau doivent être chargés")
        
        # Créer un buffer autour du réseau
        network_buffered = self.network.copy()
        network_buffered['geometry'] = network_buffered.geometry.buffer(buffer_distance)
        
        # Jointure spatiale
        joined = gpd.sjoin(self.buildings, network_buffered, how='left', predicate='within')
        
        logger.info(f"Jointure spatiale effectuée: {len(joined)} bâtiments")
        return joined
    
    def export_analysis(self, output_path: str, analysis_results: Dict):
        """
        Exporte les résultats de l'analyse dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
            analysis_results: Dictionnaire contenant les résultats
        """
        output_file = Path(output_path)
        
        # Créer le répertoire si nécessaire
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir les types numpy en types Python natifs
        def convert_to_python_types(obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_python_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_python_types(item) for item in obj]
            return obj
        
        analysis_results = convert_to_python_types(analysis_results)
        
        # Exporter en format JSON
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analyse exportée vers {output_path}")


def main():
    """Fonction principale pour démonstration."""
    analyzer = ShapefileAnalyzer()
    
    logger.info("=== Analyseur de Shapefiles pour Réseau Électrique ===")
    logger.info("Cet outil permet d'analyser les shapefiles pour la planification")
    logger.info("du raccordement électrique des bâtiments.")
    logger.info("")
    logger.info("Usage:")
    logger.info("  - Placer les shapefiles dans le répertoire 'data/'")
    logger.info("  - Noms attendus: buildings.shp, network.shp, substations.shp")
    logger.info("")
    logger.info("Pour utiliser cet analyseur dans votre code:")
    logger.info("  from analyze_shapefiles import ShapefileAnalyzer")
    logger.info("  analyzer = ShapefileAnalyzer('data')")
    logger.info("  buildings = analyzer.load_buildings('buildings.shp')")
    logger.info("  stats = analyzer.calculate_building_stats()")


if __name__ == "__main__":
    main()
