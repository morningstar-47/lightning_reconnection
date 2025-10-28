"""
Tests unitaires pour les scripts d'analyse.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter le répertoire scripts au path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from analyze_csv import CSVAnalyzer
from prioritization import PrioritizationMetric


class TestCSVAnalyzer:
    """Tests pour l'analyseur CSV."""
    
    def test_initialization(self):
        """Test l'initialisation de l'analyseur."""
        analyzer = CSVAnalyzer("data")
        assert analyzer.data_path == Path("data")
        assert analyzer.buildings_data is None
        
    def test_basic_statistics(self):
        """Test les statistiques de base."""
        analyzer = CSVAnalyzer()
        
        # Créer un DataFrame de test
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30],
            'category': ['A', 'B', 'A']
        })
        
        stats = analyzer.get_basic_statistics(df)
        assert stats['rows'] == 3
        assert stats['columns'] == 3
        assert 'value' in stats['numeric_summary']
        
    def test_identify_priority_buildings(self):
        """Test l'identification des bâtiments prioritaires."""
        analyzer = CSVAnalyzer()
        
        # Créer des données de test
        analyzer.buildings_data = pd.DataFrame({
            'building_id': [1, 2, 3, 4],
            'inhabitants': [50, 100, 25, 75],
            'priority': ['high', 'medium', 'low', 'high']
        })
        
        prioritized = analyzer.identify_priority_buildings()
        
        assert len(prioritized) == 4
        assert 'priority_score' in prioritized.columns
        # Le bâtiment avec le plus d'habitants et haute priorité devrait être premier
        assert prioritized.iloc[0]['building_id'] == 2 or prioritized.iloc[0]['building_id'] == 4
        
    def test_calculate_cost_efficiency(self):
        """Test le calcul de l'efficacité coût."""
        analyzer = CSVAnalyzer()
        
        analyzer.buildings_data = pd.DataFrame({
            'building_id': [1, 2, 3],
            'inhabitants': [50, 100, 25],
            'cost': [1000, 2000, 500]
        })
        
        result = analyzer.calculate_cost_efficiency()
        
        assert 'cost_per_inhabitant' in result.columns
        assert 'efficiency' in result.columns
        assert result['cost_per_inhabitant'].iloc[0] == 20.0  # 1000/50
        
    def test_merge_data(self):
        """Test la fusion de données."""
        analyzer = CSVAnalyzer()
        
        buildings = pd.DataFrame({
            'building_id': [1, 2, 3],
            'inhabitants': [50, 100, 25]
        })
        
        costs = pd.DataFrame({
            'building_id': [1, 2, 3],
            'cost': [1000, 2000, 500]
        })
        
        merged = analyzer.merge_data(buildings, costs, 'building_id')
        
        assert len(merged) == 3
        assert 'inhabitants' in merged.columns
        assert 'cost' in merged.columns


class TestPrioritizationMetric:
    """Tests pour les métriques de priorisation."""
    
    def test_initialization(self):
        """Test l'initialisation du système de priorisation."""
        metric = PrioritizationMetric(
            population_weight=0.4,
            cost_weight=0.3,
            urgency_weight=0.2,
            distance_weight=0.1
        )
        
        # Vérifier que les poids sont normalisés
        total = sum(metric.weights.values())
        assert abs(total - 1.0) < 0.001
        
    def test_normalize_score(self):
        """Test la normalisation des scores."""
        metric = PrioritizationMetric()
        
        values = pd.Series([10, 20, 30, 40, 50])
        normalized = metric.normalize_score(values)
        
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
        
        # Test inverse
        normalized_inv = metric.normalize_score(values, inverse=True)
        assert normalized_inv.min() == 0.0
        assert normalized_inv.max() == 1.0
        assert normalized_inv.iloc[0] == 1.0  # Plus petite valeur devient 1
        
    def test_calculate_population_score(self):
        """Test le calcul du score de population."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'inhabitants': [10, 50, 100, 25]
        })
        
        score = metric.calculate_population_score(df)
        
        assert len(score) == 4
        assert score.min() >= 0.0
        assert score.max() <= 1.0
        # Le bâtiment avec le plus d'habitants devrait avoir le score le plus élevé
        assert score.iloc[2] == 1.0  # 100 habitants
        
    def test_calculate_cost_score(self):
        """Test le calcul du score de coût."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'cost': [1000, 2000, 500, 1500]
        })
        
        score = metric.calculate_cost_score(df)
        
        assert len(score) == 4
        assert score.min() >= 0.0
        assert score.max() <= 1.0
        # Le bâtiment avec le coût le plus faible devrait avoir le score le plus élevé
        assert score.iloc[2] == 1.0  # 500 coût
        
    def test_calculate_urgency_score(self):
        """Test le calcul du score d'urgence."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'priority': ['high', 'medium', 'low', 'high'],
            'building_type': ['hospital', 'residential', 'commercial', 'school']
        })
        
        score = metric.calculate_urgency_score(df)
        
        assert len(score) == 4
        assert score.min() >= 0.0
        assert score.max() <= 1.0
        # Les hôpitaux et écoles devraient avoir un score élevé
        assert score.iloc[0] > 0.7  # hospital + high priority
        
    def test_calculate_composite_score(self):
        """Test le calcul du score composite."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'building_id': [1, 2, 3],
            'inhabitants': [50, 100, 25],
            'cost': [1000, 1500, 500],
            'priority': ['high', 'medium', 'high'],
            'distance': [50, 30, 70],
            'building_type': ['residential', 'hospital', 'residential']
        })
        
        result = metric.calculate_composite_score(df)
        
        assert 'population_score' in result.columns
        assert 'cost_score' in result.columns
        assert 'urgency_score' in result.columns
        assert 'distance_score' in result.columns
        assert 'composite_score' in result.columns
        assert 'priority_rank' in result.columns
        
        # Vérifier que les scores sont dans la plage valide
        assert result['composite_score'].min() >= 0.0
        assert result['composite_score'].max() <= 1.0
        
    def test_prioritize_buildings(self):
        """Test la priorisation des bâtiments."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'building_id': [1, 2, 3, 4],
            'inhabitants': [50, 100, 25, 75],
            'cost': [1000, 1500, 500, 800],
            'priority': ['high', 'medium', 'low', 'high'],
            'distance': [50, 30, 70, 40],
            'building_type': ['residential', 'hospital', 'commercial', 'school']
        })
        
        prioritized = metric.prioritize_buildings(df)
        
        assert len(prioritized) == 4
        assert 'composite_score' in prioritized.columns
        # Les scores devraient être triés par ordre décroissant
        scores = prioritized['composite_score'].values
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
    def test_calculate_cumulative_impact(self):
        """Test le calcul de l'impact cumulatif."""
        metric = PrioritizationMetric()
        
        df = pd.DataFrame({
            'building_id': [1, 2, 3],
            'inhabitants': [50, 100, 25],
            'cost': [1000, 1500, 500]
        })
        
        result = metric.calculate_cumulative_impact(df)
        
        assert 'cumulative_inhabitants' in result.columns
        assert 'cumulative_cost' in result.columns
        assert 'buildings_reconnected' in result.columns
        
        # Vérifier les valeurs cumulatives
        assert result['cumulative_inhabitants'].iloc[0] == 50
        assert result['cumulative_inhabitants'].iloc[1] == 150
        assert result['cumulative_inhabitants'].iloc[2] == 175


def test_imports():
    """Test que tous les modules peuvent être importés."""
    from analyze_shapefiles import ShapefileAnalyzer
    from analyze_csv import CSVAnalyzer
    from network_model import NetworkGraphModel
    from prioritization import PrioritizationMetric
    
    # Vérifier que les classes peuvent être instanciées
    assert ShapefileAnalyzer() is not None
    assert CSVAnalyzer() is not None
    assert NetworkGraphModel() is not None
    assert PrioritizationMetric() is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
