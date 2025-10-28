"""
Script principal pour l'analyse et la priorisation du raccordement électrique.
Ce script orchestre tous les outils d'analyse pour fournir un pipeline complet.
"""

import sys
from pathlib import Path
import logging
import argparse

# Ajouter le répertoire scripts au path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_shapefiles import ShapefileAnalyzer
from analyze_csv import CSVAnalyzer
from network_model import NetworkGraphModel
from prioritization import PrioritizationMetric

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ElectricalReconnectionPlanner:
    """Classe principale pour la planification du raccordement électrique."""
    
    def __init__(self, data_path: str = "data", output_path: str = "output"):
        """
        Initialise le planificateur.
        
        Args:
            data_path: Chemin vers les données
            output_path: Chemin pour les résultats
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.shapefile_analyzer = ShapefileAnalyzer(data_path)
        self.csv_analyzer = CSVAnalyzer(data_path)
        self.network_model = NetworkGraphModel()
        self.prioritization = PrioritizationMetric()
        
        logger.info(f"Planificateur initialisé (données: {data_path}, sortie: {output_path})")
    
    def run_full_analysis(self,
                         buildings_shapefile: str = "buildings.shp",
                         network_shapefile: str = "network.shp",
                         substations_shapefile: str = "substations.shp",
                         buildings_csv: str = "buildings.csv",
                         costs_csv: str = "costs.csv"):
        """
        Exécute l'analyse complète du projet de raccordement.
        
        Args:
            buildings_shapefile: Nom du shapefile des bâtiments
            network_shapefile: Nom du shapefile du réseau
            substations_shapefile: Nom du shapefile des postes
            buildings_csv: Nom du CSV des bâtiments
            costs_csv: Nom du CSV des coûts
        """
        logger.info("="*60)
        logger.info("DÉMARRAGE DE L'ANALYSE COMPLÈTE")
        logger.info("="*60)
        
        results = {}
        
        # Étape 1: Analyse des shapefiles
        logger.info("\n[Étape 1/5] Analyse des shapefiles...")
        try:
            buildings_gdf = self.shapefile_analyzer.load_buildings(buildings_shapefile)
            network_gdf = self.shapefile_analyzer.load_network(network_shapefile)
            
            try:
                substations_gdf = self.shapefile_analyzer.load_substations(substations_shapefile)
            except FileNotFoundError:
                logger.warning("Fichier des postes non trouvé, continuation sans postes")
                substations_gdf = None
            
            results['buildings_stats'] = self.shapefile_analyzer.calculate_building_stats()
            results['network_stats'] = self.shapefile_analyzer.calculate_network_stats()
            
            logger.info("✓ Analyse des shapefiles terminée")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'analyse des shapefiles: {e}")
            buildings_gdf = None
            network_gdf = None
            substations_gdf = None
        
        # Étape 2: Analyse des CSV
        logger.info("\n[Étape 2/5] Analyse des fichiers CSV...")
        try:
            buildings_df = self.csv_analyzer.load_buildings_data(buildings_csv)
            
            try:
                costs_df = self.csv_analyzer.load_costs_data(costs_csv)
            except FileNotFoundError:
                logger.warning("Fichier des coûts non trouvé, continuation sans coûts")
                costs_df = None
            
            results['csv_buildings_stats'] = self.csv_analyzer.analyze_buildings()
            
            if costs_df is not None:
                results['csv_costs_stats'] = self.csv_analyzer.analyze_costs()
            
            logger.info("✓ Analyse des CSV terminée")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'analyse des CSV: {e}")
            buildings_df = None
            costs_df = None
        
        # Étape 3: Modélisation du réseau en graphe
        logger.info("\n[Étape 3/5] Modélisation du réseau en graphe...")
        if buildings_gdf is not None and network_gdf is not None:
            try:
                graph = self.network_model.build_graph_from_geodataframes(
                    network_gdf, buildings_gdf, substations_gdf
                )
                
                results['graph_stats'] = self.network_model.calculate_network_statistics()
                
                # Identifier les nœuds critiques
                critical_nodes = self.network_model.identify_critical_nodes(top_n=10)
                results['critical_nodes'] = [
                    {'node': str(node), 'centrality': float(centrality)}
                    for node, centrality in critical_nodes
                ]
                
                # Exporter le graphe
                graph_output = self.output_path / "network_graph.gexf"
                self.network_model.export_graph(graph_output)
                
                # Visualiser le graphe
                viz_output = self.output_path / "network_visualization.png"
                self.network_model.visualize_graph(viz_output)
                
                logger.info("✓ Modélisation du réseau terminée")
            except Exception as e:
                logger.error(f"✗ Erreur lors de la modélisation du réseau: {e}")
        else:
            logger.warning("✗ Modélisation du réseau ignorée (données manquantes)")
        
        # Étape 4: Calcul des métriques de priorisation
        logger.info("\n[Étape 4/5] Calcul des métriques de priorisation...")
        if buildings_df is not None:
            try:
                # Fusionner les données si possible
                if costs_df is not None:
                    merged_df = self.csv_analyzer.merge_data(buildings_df, costs_df)
                else:
                    merged_df = buildings_df
                
                # Calculer les priorités
                prioritized_df = self.prioritization.prioritize_buildings(merged_df)
                
                # Calculer l'impact cumulatif
                cumulative_df = self.prioritization.calculate_cumulative_impact(prioritized_df)
                
                # Générer le rapport
                report_output = self.output_path / "prioritization_report.json"
                results['prioritization_report'] = self.prioritization.generate_priority_report(
                    cumulative_df, report_output
                )
                
                # Exporter le DataFrame priorisé
                prioritized_output = self.output_path / "prioritized_buildings.csv"
                self.csv_analyzer.export_dataframe(cumulative_df, prioritized_output)
                
                logger.info("✓ Calcul des métriques de priorisation terminé")
            except Exception as e:
                logger.error(f"✗ Erreur lors du calcul de priorisation: {e}")
        else:
            logger.warning("✗ Calcul de priorisation ignoré (données manquantes)")
        
        # Étape 5: Génération du rapport final
        logger.info("\n[Étape 5/5] Génération du rapport final...")
        try:
            report_output = self.output_path / "analysis_report.json"
            self.shapefile_analyzer.export_analysis(report_output, results)
            
            # Générer un résumé textuel
            summary_output = self.output_path / "summary.txt"
            self._generate_summary(results, summary_output)
            
            logger.info("✓ Rapport final généré")
        except Exception as e:
            logger.error(f"✗ Erreur lors de la génération du rapport: {e}")
        
        logger.info("\n" + "="*60)
        logger.info("ANALYSE COMPLÈTE TERMINÉE")
        logger.info(f"Résultats disponibles dans: {self.output_path}")
        logger.info("="*60)
        
        return results
    
    def _generate_summary(self, results: dict, output_path: Path):
        """
        Génère un résumé textuel de l'analyse.
        
        Args:
            results: Dictionnaire des résultats
            output_path: Chemin du fichier de sortie
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RÉSUMÉ DE L'ANALYSE DU RACCORDEMENT ÉLECTRIQUE\n")
            f.write("="*60 + "\n\n")
            
            # Statistiques des bâtiments
            if 'buildings_stats' in results:
                stats = results['buildings_stats']
                f.write("BÂTIMENTS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Nombre total: {stats.get('count', 'N/A')}\n")
                
                if 'total_inhabitants' in stats:
                    f.write(f"Population totale: {stats['total_inhabitants']} habitants\n")
                    f.write(f"Moyenne par bâtiment: {stats['mean_inhabitants']:.1f} habitants\n")
                
                f.write("\n")
            
            # Statistiques du réseau
            if 'network_stats' in results:
                stats = results['network_stats']
                f.write("RÉSEAU ÉLECTRIQUE\n")
                f.write("-" * 40 + "\n")
                f.write(f"Nombre de segments: {stats.get('count', 'N/A')}\n")
                
                if 'total_length' in stats:
                    f.write(f"Longueur totale: {stats['total_length']:.2f} unités\n")
                
                if 'status_counts' in stats:
                    f.write("Statut du réseau:\n")
                    for status, count in stats['status_counts'].items():
                        f.write(f"  - {status}: {count}\n")
                
                f.write("\n")
            
            # Statistiques du graphe
            if 'graph_stats' in results:
                stats = results['graph_stats']
                f.write("MODÈLE DE GRAPHE\n")
                f.write("-" * 40 + "\n")
                f.write(f"Nœuds: {stats.get('nodes', 'N/A')}\n")
                f.write(f"Arêtes: {stats.get('edges', 'N/A')}\n")
                f.write(f"Réseau connecté: {'Oui' if stats.get('is_connected', False) else 'Non'}\n")
                
                if 'node_types' in stats:
                    f.write("Types de nœuds:\n")
                    for node_type, count in stats['node_types'].items():
                        f.write(f"  - {node_type}: {count}\n")
                
                f.write("\n")
            
            # Rapport de priorisation
            if 'prioritization_report' in results:
                report = results['prioritization_report']
                f.write("PRIORISATION\n")
                f.write("-" * 40 + "\n")
                f.write(f"Bâtiments analysés: {report.get('total_buildings', 'N/A')}\n")
                
                if 'top_20_percent' in report:
                    top20 = report['top_20_percent']
                    f.write(f"\nTop 20% des bâtiments prioritaires:\n")
                    f.write(f"  - Nombre: {top20['buildings']}\n")
                    f.write(f"  - Habitants couverts: {top20['inhabitants_covered']}\n")
                    f.write(f"  - Coût total: {top20['total_cost']:.2f}\n")
                
                f.write("\n")
            
            f.write("="*60 + "\n")
            f.write(f"Fichiers de sortie générés dans: {self.output_path}\n")
            f.write("="*60 + "\n")
        
        logger.info(f"Résumé textuel sauvegardé: {output_path}")


def main():
    """Fonction principale avec arguments en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Planification du raccordement électrique après intempéries"
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default='data',
        help='Chemin vers le répertoire des données (défaut: data)'
    )
    
    parser.add_argument(
        '--output-path',
        type=str,
        default='output',
        help='Chemin vers le répertoire de sortie (défaut: output)'
    )
    
    parser.add_argument(
        '--buildings-shp',
        type=str,
        default='buildings.shp',
        help='Nom du shapefile des bâtiments'
    )
    
    parser.add_argument(
        '--network-shp',
        type=str,
        default='network.shp',
        help='Nom du shapefile du réseau'
    )
    
    parser.add_argument(
        '--substations-shp',
        type=str,
        default='substations.shp',
        help='Nom du shapefile des postes'
    )
    
    parser.add_argument(
        '--buildings-csv',
        type=str,
        default='buildings.csv',
        help='Nom du CSV des bâtiments'
    )
    
    parser.add_argument(
        '--costs-csv',
        type=str,
        default='costs.csv',
        help='Nom du CSV des coûts'
    )
    
    args = parser.parse_args()
    
    # Créer le planificateur
    planner = ElectricalReconnectionPlanner(args.data_path, args.output_path)
    
    # Exécuter l'analyse complète
    planner.run_full_analysis(
        buildings_shapefile=args.buildings_shp,
        network_shapefile=args.network_shp,
        substations_shapefile=args.substations_shp,
        buildings_csv=args.buildings_csv,
        costs_csv=args.costs_csv
    )


if __name__ == "__main__":
    main()
