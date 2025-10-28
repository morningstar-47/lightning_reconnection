"""
Script pour l'analyse des fichiers CSV.
Ce script permet de charger, analyser et traiter des données CSV
contenant des informations sur les bâtiments, leur priorité,
et les coûts de raccordement.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CSVAnalyzer:
    """Classe pour analyser les données CSV des bâtiments et du réseau."""
    
    def __init__(self, data_path: str = "data"):
        """
        Initialise l'analyseur de CSV.
        
        Args:
            data_path: Chemin vers le répertoire contenant les fichiers CSV
        """
        self.data_path = Path(data_path)
        self.buildings_data = None
        self.network_data = None
        self.costs_data = None
        
    def load_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Charge un fichier CSV.
        
        Args:
            filename: Nom du fichier CSV
            **kwargs: Arguments supplémentaires pour pd.read_csv
            
        Returns:
            DataFrame contenant les données du CSV
        """
        filepath = self.data_path / filename
        
        if not filepath.exists():
            logger.error(f"Le fichier {filepath} n'existe pas")
            raise FileNotFoundError(f"Le fichier {filepath} n'existe pas")
        
        try:
            df = pd.read_csv(filepath, **kwargs)
            logger.info(f"CSV chargé: {filename} ({len(df)} lignes, {len(df.columns)} colonnes)")
            return df
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filename}: {str(e)}")
            raise
    
    def load_buildings_data(self, filename: str = "buildings.csv") -> pd.DataFrame:
        """
        Charge le fichier CSV des bâtiments.
        
        Args:
            filename: Nom du fichier CSV des bâtiments
            
        Returns:
            DataFrame des bâtiments
        """
        self.buildings_data = self.load_csv(filename)
        logger.info(f"Données des bâtiments chargées: {len(self.buildings_data)} bâtiments")
        return self.buildings_data
    
    def load_network_data(self, filename: str = "network.csv") -> pd.DataFrame:
        """
        Charge le fichier CSV du réseau électrique.
        
        Args:
            filename: Nom du fichier CSV du réseau
            
        Returns:
            DataFrame du réseau électrique
        """
        self.network_data = self.load_csv(filename)
        logger.info(f"Données du réseau chargées: {len(self.network_data)} segments")
        return self.network_data
    
    def load_costs_data(self, filename: str = "costs.csv") -> pd.DataFrame:
        """
        Charge le fichier CSV des coûts.
        
        Args:
            filename: Nom du fichier CSV des coûts
            
        Returns:
            DataFrame des coûts
        """
        self.costs_data = self.load_csv(filename)
        logger.info(f"Données des coûts chargées: {len(self.costs_data)} entrées")
        return self.costs_data
    
    def get_basic_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calcule des statistiques de base sur un DataFrame.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire contenant les statistiques
        """
        stats = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        # Statistiques descriptives pour les colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Statistiques pour les colonnes catégorielles
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            stats['categorical_summary'] = {}
            for col in categorical_cols:
                stats['categorical_summary'][col] = df[col].value_counts().to_dict()
        
        return stats
    
    def analyze_buildings(self) -> Dict:
        """
        Analyse les données des bâtiments.
        
        Returns:
            Dictionnaire contenant l'analyse des bâtiments
        """
        if self.buildings_data is None:
            raise ValueError("Les données des bâtiments n'ont pas été chargées")
        
        analysis = self.get_basic_statistics(self.buildings_data)
        
        # Analyse spécifique aux bâtiments
        df = self.buildings_data
        
        # Population totale
        if 'inhabitants' in df.columns:
            analysis['total_inhabitants'] = int(df['inhabitants'].sum())
            analysis['mean_inhabitants'] = float(df['inhabitants'].mean())
            analysis['median_inhabitants'] = float(df['inhabitants'].median())
        
        # Types de bâtiments
        if 'building_type' in df.columns:
            analysis['building_types'] = df['building_type'].value_counts().to_dict()
        
        # Statut de connexion
        if 'connected' in df.columns:
            analysis['connection_status'] = df['connected'].value_counts().to_dict()
            analysis['disconnected_count'] = int((df['connected'] == False).sum())
            analysis['disconnected_percentage'] = float((df['connected'] == False).sum() / len(df) * 100)
        
        # Priorité
        if 'priority' in df.columns:
            analysis['priority_distribution'] = df['priority'].value_counts().to_dict()
            analysis['high_priority_count'] = int((df['priority'] == 'high').sum() if 'high' in df['priority'].values else 0)
        
        return analysis
    
    def analyze_costs(self) -> Dict:
        """
        Analyse les données des coûts de raccordement.
        
        Returns:
            Dictionnaire contenant l'analyse des coûts
        """
        if self.costs_data is None:
            raise ValueError("Les données des coûts n'ont pas été chargées")
        
        analysis = self.get_basic_statistics(self.costs_data)
        
        df = self.costs_data
        
        # Coûts totaux et moyens
        if 'cost' in df.columns:
            analysis['total_cost'] = float(df['cost'].sum())
            analysis['mean_cost'] = float(df['cost'].mean())
            analysis['median_cost'] = float(df['cost'].median())
            analysis['min_cost'] = float(df['cost'].min())
            analysis['max_cost'] = float(df['cost'].max())
        
        # Distance de raccordement
        if 'distance' in df.columns:
            analysis['total_distance'] = float(df['distance'].sum())
            analysis['mean_distance'] = float(df['distance'].mean())
        
        return analysis
    
    def identify_priority_buildings(self, 
                                   priority_column: str = 'priority',
                                   inhabitants_column: str = 'inhabitants') -> pd.DataFrame:
        """
        Identifie les bâtiments prioritaires pour le raccordement.
        
        Args:
            priority_column: Nom de la colonne de priorité
            inhabitants_column: Nom de la colonne du nombre d'habitants
            
        Returns:
            DataFrame des bâtiments prioritaires triés
        """
        if self.buildings_data is None:
            raise ValueError("Les données des bâtiments n'ont pas été chargées")
        
        df = self.buildings_data.copy()
        
        # Créer un score de priorité
        priority_score = pd.Series(0, index=df.index)
        
        # Score basé sur la priorité explicite
        if priority_column in df.columns:
            priority_map = {'high': 3, 'medium': 2, 'low': 1}
            priority_score += df[priority_column].map(priority_map).fillna(0)
        
        # Score basé sur le nombre d'habitants
        if inhabitants_column in df.columns:
            # Normaliser entre 0 et 1, puis multiplier par 3
            max_inhabitants = df[inhabitants_column].max()
            if max_inhabitants > 0:
                priority_score += (df[inhabitants_column] / max_inhabitants) * 3
        
        df['priority_score'] = priority_score
        df_sorted = df.sort_values('priority_score', ascending=False)
        
        logger.info(f"Bâtiments prioritaires identifiés: {len(df_sorted)} bâtiments triés")
        return df_sorted
    
    def calculate_cost_efficiency(self, 
                                  cost_column: str = 'cost',
                                  inhabitants_column: str = 'inhabitants') -> pd.DataFrame:
        """
        Calcule l'efficacité coût par habitant pour chaque bâtiment.
        
        Args:
            cost_column: Nom de la colonne de coût
            inhabitants_column: Nom de la colonne du nombre d'habitants
            
        Returns:
            DataFrame avec la métrique d'efficacité ajoutée
        """
        if self.buildings_data is None:
            raise ValueError("Les données des bâtiments n'ont pas été chargées")
        
        df = self.buildings_data.copy()
        
        if cost_column in df.columns and inhabitants_column in df.columns:
            # Coût par habitant (plus c'est bas, mieux c'est)
            df['cost_per_inhabitant'] = df[cost_column] / df[inhabitants_column].replace(0, 1)
            
            # Efficacité (inverse du coût par habitant)
            df['efficiency'] = 1 / (df['cost_per_inhabitant'] + 1)
            
            logger.info("Métrique d'efficacité coût calculée")
        else:
            logger.warning(f"Colonnes {cost_column} ou {inhabitants_column} non trouvées")
        
        return df
    
    def merge_data(self, 
                  buildings_df: Optional[pd.DataFrame] = None,
                  costs_df: Optional[pd.DataFrame] = None,
                  on_column: str = 'building_id') -> pd.DataFrame:
        """
        Fusionne les données de plusieurs DataFrames.
        
        Args:
            buildings_df: DataFrame des bâtiments
            costs_df: DataFrame des coûts
            on_column: Colonne pour la fusion
            
        Returns:
            DataFrame fusionné
        """
        buildings = buildings_df if buildings_df is not None else self.buildings_data
        costs = costs_df if costs_df is not None else self.costs_data
        
        if buildings is None:
            raise ValueError("Aucune donnée de bâtiments disponible")
        
        if costs is None:
            logger.warning("Aucune donnée de coûts disponible, retour des données de bâtiments")
            return buildings
        
        # Fusion
        if on_column in buildings.columns and on_column in costs.columns:
            merged = pd.merge(buildings, costs, on=on_column, how='left')
            logger.info(f"Données fusionnées: {len(merged)} lignes")
        else:
            logger.warning(f"Colonne {on_column} non trouvée dans les deux DataFrames")
            merged = buildings
        
        return merged
    
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
        
        # Exporter en format JSON
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analyse exportée vers {output_path}")
    
    def export_dataframe(self, df: pd.DataFrame, output_path: str, format: str = 'csv'):
        """
        Exporte un DataFrame dans un fichier.
        
        Args:
            df: DataFrame à exporter
            output_path: Chemin du fichier de sortie
            format: Format de sortie ('csv', 'excel', 'json')
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'csv':
            df.to_csv(output_file, index=False, encoding='utf-8')
        elif format == 'excel':
            df.to_excel(output_file, index=False)
        elif format == 'json':
            df.to_json(output_file, orient='records', indent=2, force_ascii=False)
        else:
            raise ValueError(f"Format {format} non supporté")
        
        logger.info(f"DataFrame exporté vers {output_path}")


def main():
    """Fonction principale pour démonstration."""
    analyzer = CSVAnalyzer()
    
    logger.info("=== Analyseur de CSV pour Données de Raccordement Électrique ===")
    logger.info("Cet outil permet d'analyser les données CSV pour la planification")
    logger.info("du raccordement électrique des bâtiments.")
    logger.info("")
    logger.info("Usage:")
    logger.info("  - Placer les fichiers CSV dans le répertoire 'data/'")
    logger.info("  - Noms attendus: buildings.csv, network.csv, costs.csv")
    logger.info("")
    logger.info("Pour utiliser cet analyseur dans votre code:")
    logger.info("  from analyze_csv import CSVAnalyzer")
    logger.info("  analyzer = CSVAnalyzer('data')")
    logger.info("  buildings = analyzer.load_buildings_data('buildings.csv')")
    logger.info("  analysis = analyzer.analyze_buildings()")


if __name__ == "__main__":
    main()
