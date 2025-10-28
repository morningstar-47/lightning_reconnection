"""
Script pour le développement de la métrique de priorisation.
Ce script implémente différentes métriques pour prioriser le raccordement
des bâtiments en fonction de plusieurs critères.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PrioritizationMetric:
    """Classe pour calculer les métriques de priorisation des raccordements."""
    
    def __init__(self, 
                 population_weight: float = 0.4,
                 cost_weight: float = 0.3,
                 urgency_weight: float = 0.2,
                 distance_weight: float = 0.1):
        """
        Initialise le système de priorisation.
        
        Args:
            population_weight: Poids du critère population (0-1)
            cost_weight: Poids du critère coût (0-1)
            urgency_weight: Poids du critère urgence (0-1)
            distance_weight: Poids du critère distance (0-1)
        """
        # Normaliser les poids pour qu'ils somment à 1
        total = population_weight + cost_weight + urgency_weight + distance_weight
        
        self.weights = {
            'population': population_weight / total,
            'cost': cost_weight / total,
            'urgency': urgency_weight / total,
            'distance': distance_weight / total
        }
        
        logger.info(f"Système de priorisation initialisé avec les poids: {self.weights}")
    
    def normalize_score(self, values: pd.Series, inverse: bool = False) -> pd.Series:
        """
        Normalise un score entre 0 et 1.
        
        Args:
            values: Série de valeurs à normaliser
            inverse: Si True, inverse les valeurs (pour les coûts, distances)
            
        Returns:
            Série normalisée
        """
        min_val = values.min()
        max_val = values.max()
        
        if max_val == min_val:
            return pd.Series(0.5, index=values.index)
        
        normalized = (values - min_val) / (max_val - min_val)
        
        if inverse:
            normalized = 1 - normalized
        
        return normalized
    
    def calculate_population_score(self, df: pd.DataFrame, inhabitants_col: str = 'inhabitants') -> pd.Series:
        """
        Calcule le score basé sur la population.
        Plus il y a d'habitants, plus le score est élevé.
        
        Args:
            df: DataFrame contenant les données
            inhabitants_col: Nom de la colonne du nombre d'habitants
            
        Returns:
            Série de scores normalisés
        """
        if inhabitants_col not in df.columns:
            logger.warning(f"Colonne {inhabitants_col} non trouvée, score de population mis à 0")
            return pd.Series(0, index=df.index)
        
        # Normaliser entre 0 et 1 (plus d'habitants = score plus élevé)
        score = self.normalize_score(df[inhabitants_col], inverse=False)
        
        logger.info(f"Score de population calculé (min: {score.min():.3f}, max: {score.max():.3f})")
        return score
    
    def calculate_cost_score(self, df: pd.DataFrame, cost_col: str = 'cost') -> pd.Series:
        """
        Calcule le score basé sur le coût.
        Plus le coût est faible, plus le score est élevé.
        
        Args:
            df: DataFrame contenant les données
            cost_col: Nom de la colonne du coût
            
        Returns:
            Série de scores normalisés
        """
        if cost_col not in df.columns:
            logger.warning(f"Colonne {cost_col} non trouvée, score de coût mis à 0.5")
            return pd.Series(0.5, index=df.index)
        
        # Normaliser entre 0 et 1 (coût plus faible = score plus élevé)
        score = self.normalize_score(df[cost_col], inverse=True)
        
        logger.info(f"Score de coût calculé (min: {score.min():.3f}, max: {score.max():.3f})")
        return score
    
    def calculate_urgency_score(self, df: pd.DataFrame, 
                               priority_col: Optional[str] = 'priority',
                               building_type_col: Optional[str] = 'building_type') -> pd.Series:
        """
        Calcule le score basé sur l'urgence.
        Prend en compte la priorité explicite et le type de bâtiment.
        
        Args:
            df: DataFrame contenant les données
            priority_col: Nom de la colonne de priorité
            building_type_col: Nom de la colonne du type de bâtiment
            
        Returns:
            Série de scores normalisés
        """
        score = pd.Series(0.5, index=df.index)  # Score par défaut
        
        # Score basé sur la priorité explicite
        if priority_col and priority_col in df.columns:
            priority_map = {
                'high': 1.0,
                'critical': 1.0,
                'élevée': 1.0,
                'critique': 1.0,
                'medium': 0.6,
                'moyenne': 0.6,
                'low': 0.2,
                'faible': 0.2
            }
            
            priority_score = df[priority_col].map(priority_map).fillna(0.5)
            score = score * 0.5 + priority_score * 0.5
        
        # Bonus pour les bâtiments critiques (hôpitaux, écoles, etc.)
        if building_type_col and building_type_col in df.columns:
            critical_types = ['hospital', 'hôpital', 'school', 'école', 'emergency', 'urgence']
            
            type_bonus = df[building_type_col].apply(
                lambda x: 0.3 if isinstance(x, str) and any(ct in x.lower() for ct in critical_types) else 0
            )
            
            score = score + type_bonus
            score = score.clip(0, 1)  # Limiter entre 0 et 1
        
        logger.info(f"Score d'urgence calculé (min: {score.min():.3f}, max: {score.max():.3f})")
        return score
    
    def calculate_distance_score(self, df: pd.DataFrame, distance_col: str = 'distance') -> pd.Series:
        """
        Calcule le score basé sur la distance.
        Plus la distance est courte, plus le score est élevé.
        
        Args:
            df: DataFrame contenant les données
            distance_col: Nom de la colonne de distance
            
        Returns:
            Série de scores normalisés
        """
        if distance_col not in df.columns:
            logger.warning(f"Colonne {distance_col} non trouvée, score de distance mis à 0.5")
            return pd.Series(0.5, index=df.index)
        
        # Normaliser entre 0 et 1 (distance plus courte = score plus élevé)
        score = self.normalize_score(df[distance_col], inverse=True)
        
        logger.info(f"Score de distance calculé (min: {score.min():.3f}, max: {score.max():.3f})")
        return score
    
    def calculate_efficiency_score(self, df: pd.DataFrame,
                                   inhabitants_col: str = 'inhabitants',
                                   cost_col: str = 'cost') -> pd.Series:
        """
        Calcule un score d'efficacité (habitants / coût).
        
        Args:
            df: DataFrame contenant les données
            inhabitants_col: Nom de la colonne du nombre d'habitants
            cost_col: Nom de la colonne du coût
            
        Returns:
            Série de scores normalisés
        """
        if inhabitants_col not in df.columns or cost_col not in df.columns:
            logger.warning("Colonnes nécessaires non trouvées pour le score d'efficacité")
            return pd.Series(0.5, index=df.index)
        
        # Calculer l'efficacité (habitants par unité de coût)
        efficiency = df[inhabitants_col] / (df[cost_col] + 1)  # +1 pour éviter division par 0
        
        # Normaliser
        score = self.normalize_score(efficiency, inverse=False)
        
        logger.info(f"Score d'efficacité calculé (min: {score.min():.3f}, max: {score.max():.3f})")
        return score
    
    def calculate_composite_score(self, df: pd.DataFrame,
                                  inhabitants_col: str = 'inhabitants',
                                  cost_col: str = 'cost',
                                  priority_col: Optional[str] = 'priority',
                                  distance_col: str = 'distance',
                                  building_type_col: Optional[str] = 'building_type') -> pd.DataFrame:
        """
        Calcule un score composite basé sur tous les critères.
        
        Args:
            df: DataFrame contenant les données
            inhabitants_col: Nom de la colonne du nombre d'habitants
            cost_col: Nom de la colonne du coût
            priority_col: Nom de la colonne de priorité
            distance_col: Nom de la colonne de distance
            building_type_col: Nom de la colonne du type de bâtiment
            
        Returns:
            DataFrame avec les scores ajoutés
        """
        result_df = df.copy()
        
        # Calculer les scores individuels
        logger.info("Calcul des scores individuels...")
        
        result_df['population_score'] = self.calculate_population_score(df, inhabitants_col)
        result_df['cost_score'] = self.calculate_cost_score(df, cost_col)
        result_df['urgency_score'] = self.calculate_urgency_score(df, priority_col, building_type_col)
        result_df['distance_score'] = self.calculate_distance_score(df, distance_col)
        
        # Calculer le score composite pondéré
        logger.info("Calcul du score composite...")
        result_df['composite_score'] = (
            result_df['population_score'] * self.weights['population'] +
            result_df['cost_score'] * self.weights['cost'] +
            result_df['urgency_score'] * self.weights['urgency'] +
            result_df['distance_score'] * self.weights['distance']
        )
        
        # Ajouter un rang
        result_df['priority_rank'] = result_df['composite_score'].rank(ascending=False, method='min').astype(int)
        
        logger.info(f"Score composite calculé (min: {result_df['composite_score'].min():.3f}, "
                   f"max: {result_df['composite_score'].max():.3f})")
        
        return result_df
    
    def prioritize_buildings(self, df: pd.DataFrame,
                            inhabitants_col: str = 'inhabitants',
                            cost_col: str = 'cost',
                            priority_col: Optional[str] = 'priority',
                            distance_col: str = 'distance',
                            building_type_col: Optional[str] = 'building_type',
                            top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Priorise les bâtiments selon les métriques calculées.
        
        Args:
            df: DataFrame contenant les données des bâtiments
            inhabitants_col: Nom de la colonne du nombre d'habitants
            cost_col: Nom de la colonne du coût
            priority_col: Nom de la colonne de priorité
            distance_col: Nom de la colonne de distance
            building_type_col: Nom de la colonne du type de bâtiment
            top_n: Nombre de bâtiments à retourner (tous si None)
            
        Returns:
            DataFrame trié par priorité
        """
        # Calculer les scores
        scored_df = self.calculate_composite_score(
            df, inhabitants_col, cost_col, priority_col, distance_col, building_type_col
        )
        
        # Trier par score composite
        sorted_df = scored_df.sort_values('composite_score', ascending=False)
        
        # Retourner le top N si spécifié
        if top_n:
            sorted_df = sorted_df.head(top_n)
        
        logger.info(f"Priorisation terminée: {len(sorted_df)} bâtiments triés")
        
        return sorted_df
    
    def calculate_cumulative_impact(self, prioritized_df: pd.DataFrame,
                                   inhabitants_col: str = 'inhabitants',
                                   cost_col: str = 'cost') -> pd.DataFrame:
        """
        Calcule l'impact cumulatif du raccordement selon l'ordre de priorité.
        
        Args:
            prioritized_df: DataFrame des bâtiments priorisés
            inhabitants_col: Nom de la colonne du nombre d'habitants
            cost_col: Nom de la colonne du coût
            
        Returns:
            DataFrame avec les métriques cumulatives
        """
        result_df = prioritized_df.copy()
        
        if inhabitants_col in result_df.columns:
            result_df['cumulative_inhabitants'] = result_df[inhabitants_col].cumsum()
            result_df['cumulative_inhabitants_pct'] = (
                result_df['cumulative_inhabitants'] / result_df[inhabitants_col].sum() * 100
            )
        
        if cost_col in result_df.columns:
            result_df['cumulative_cost'] = result_df[cost_col].cumsum()
            result_df['cumulative_cost_pct'] = (
                result_df['cumulative_cost'] / result_df[cost_col].sum() * 100
            )
        
        result_df['buildings_reconnected'] = range(1, len(result_df) + 1)
        result_df['buildings_reconnected_pct'] = (
            result_df['buildings_reconnected'] / len(result_df) * 100
        )
        
        logger.info("Impact cumulatif calculé")
        
        return result_df
    
    def generate_priority_report(self, prioritized_df: pd.DataFrame,
                                output_path: Optional[str] = None) -> Dict:
        """
        Génère un rapport de priorisation.
        
        Args:
            prioritized_df: DataFrame des bâtiments priorisés
            output_path: Chemin pour sauvegarder le rapport (optionnel)
            
        Returns:
            Dictionnaire contenant le rapport
        """
        report = {
            'total_buildings': len(prioritized_df),
            'top_10_buildings': prioritized_df.head(10).to_dict('records')
        }
        
        # Statistiques sur les scores
        score_cols = [col for col in prioritized_df.columns if 'score' in col]
        for col in score_cols:
            report[f'{col}_stats'] = {
                'mean': float(prioritized_df[col].mean()),
                'median': float(prioritized_df[col].median()),
                'std': float(prioritized_df[col].std()),
                'min': float(prioritized_df[col].min()),
                'max': float(prioritized_df[col].max())
            }
        
        # Statistiques cumulatives si disponibles
        if 'cumulative_inhabitants' in prioritized_df.columns:
            # Top 20% des bâtiments
            top_20_pct = int(len(prioritized_df) * 0.2)
            top_20_df = prioritized_df.head(top_20_pct)
            
            report['top_20_percent'] = {
                'buildings': top_20_pct,
                'inhabitants_covered': int(top_20_df['inhabitants'].sum()) if 'inhabitants' in top_20_df.columns else 0,
                'total_cost': float(top_20_df['cost'].sum()) if 'cost' in top_20_df.columns else 0
            }
        
        if output_path:
            import json
            from pathlib import Path
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Rapport de priorisation exporté vers {output_path}")
        
        return report


def main():
    """Fonction principale pour démonstration."""
    logger.info("=== Système de Priorisation pour Raccordement Électrique ===")
    logger.info("Cet outil permet de calculer des métriques de priorisation")
    logger.info("pour optimiser l'ordre de raccordement des bâtiments.")
    logger.info("")
    logger.info("Usage:")
    logger.info("  from prioritization import PrioritizationMetric")
    logger.info("  metric = PrioritizationMetric(population_weight=0.4, cost_weight=0.3)")
    logger.info("  prioritized = metric.prioritize_buildings(df)")
    logger.info("")
    logger.info("Critères de priorisation:")
    logger.info("  - Population: nombre d'habitants affectés")
    logger.info("  - Coût: coût du raccordement")
    logger.info("  - Urgence: priorité et type de bâtiment")
    logger.info("  - Distance: distance au réseau existant")


if __name__ == "__main__":
    main()
