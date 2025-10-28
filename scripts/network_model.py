"""
Script pour la modélisation du réseau électrique en graphe.
Ce script utilise NetworkX pour modéliser le réseau électrique et
calculer les chemins optimaux de raccordement.
"""

import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
from typing import Dict, List, Tuple, Optional, Set
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NetworkGraphModel:
    """Classe pour modéliser le réseau électrique comme un graphe."""
    
    def __init__(self):
        """Initialise le modèle de graphe du réseau."""
        self.graph = nx.Graph()
        self.buildings = None
        self.network = None
        self.substations = None
        self.node_positions = {}
        
    def build_graph_from_geodataframes(self,
                                      network_gdf: gpd.GeoDataFrame,
                                      buildings_gdf: Optional[gpd.GeoDataFrame] = None,
                                      substations_gdf: Optional[gpd.GeoDataFrame] = None) -> nx.Graph:
        """
        Construit un graphe à partir de GeoDataFrames.
        
        Args:
            network_gdf: GeoDataFrame du réseau électrique (lignes)
            buildings_gdf: GeoDataFrame des bâtiments (points)
            substations_gdf: GeoDataFrame des postes de transformation (points)
            
        Returns:
            Graphe NetworkX du réseau
        """
        self.network = network_gdf
        self.buildings = buildings_gdf
        self.substations = substations_gdf
        
        # Ajouter les segments du réseau comme arêtes
        logger.info("Construction du graphe à partir du réseau...")
        for idx, row in network_gdf.iterrows():
            geom = row.geometry
            
            if geom.geom_type == 'LineString':
                # Extraire les points de début et de fin
                start_point = (geom.coords[0][0], geom.coords[0][1])
                end_point = (geom.coords[-1][0], geom.coords[-1][1])
                
                # Ajouter les nœuds si nécessaire
                if start_point not in self.graph:
                    self.graph.add_node(start_point, x=start_point[0], y=start_point[1], type='network')
                    self.node_positions[start_point] = start_point
                    
                if end_point not in self.graph:
                    self.graph.add_node(end_point, x=end_point[0], y=end_point[1], type='network')
                    self.node_positions[end_point] = end_point
                
                # Calculer les attributs de l'arête
                length = geom.length
                weight = length
                
                # Ajouter des poids supplémentaires si disponibles
                edge_attrs = {
                    'length': length,
                    'weight': weight,
                    'segment_id': idx
                }
                
                if 'status' in row:
                    edge_attrs['status'] = row['status']
                    # Si endommagé, augmenter le poids
                    if row['status'] == 'damaged':
                        edge_attrs['weight'] = length * 10
                
                if 'capacity' in row:
                    edge_attrs['capacity'] = row['capacity']
                
                # Ajouter l'arête
                self.graph.add_edge(start_point, end_point, **edge_attrs)
        
        logger.info(f"Graphe construit: {self.graph.number_of_nodes()} nœuds, {self.graph.number_of_edges()} arêtes")
        
        # Ajouter les postes de transformation comme nœuds spéciaux
        if substations_gdf is not None:
            self._add_substations_to_graph(substations_gdf)
        
        # Ajouter les bâtiments comme nœuds
        if buildings_gdf is not None:
            self._add_buildings_to_graph(buildings_gdf)
        
        return self.graph
    
    def _add_substations_to_graph(self, substations_gdf: gpd.GeoDataFrame):
        """
        Ajoute les postes de transformation au graphe.
        
        Args:
            substations_gdf: GeoDataFrame des postes
        """
        logger.info("Ajout des postes de transformation au graphe...")
        
        for idx, row in substations_gdf.iterrows():
            point = row.geometry
            node_id = f"substation_{idx}"
            coords = (point.x, point.y)
            
            node_attrs = {
                'x': coords[0],
                'y': coords[1],
                'type': 'substation',
                'substation_id': idx
            }
            
            if 'capacity' in row:
                node_attrs['capacity'] = row['capacity']
            
            if 'name' in row:
                node_attrs['name'] = row['name']
            
            self.graph.add_node(node_id, **node_attrs)
            self.node_positions[node_id] = coords
            
            # Connecter au nœud du réseau le plus proche
            self._connect_to_nearest_network_node(node_id, coords)
        
        logger.info(f"{len(substations_gdf)} postes ajoutés au graphe")
    
    def _add_buildings_to_graph(self, buildings_gdf: gpd.GeoDataFrame):
        """
        Ajoute les bâtiments au graphe.
        
        Args:
            buildings_gdf: GeoDataFrame des bâtiments
        """
        logger.info("Ajout des bâtiments au graphe...")
        
        for idx, row in buildings_gdf.iterrows():
            point = row.geometry
            node_id = f"building_{idx}"
            coords = (point.x, point.y)
            
            node_attrs = {
                'x': coords[0],
                'y': coords[1],
                'type': 'building',
                'building_id': idx
            }
            
            if 'inhabitants' in row:
                node_attrs['inhabitants'] = row['inhabitants']
            
            if 'connected' in row:
                node_attrs['connected'] = row['connected']
            
            if 'priority' in row:
                node_attrs['priority'] = row['priority']
            
            self.graph.add_node(node_id, **node_attrs)
            self.node_positions[node_id] = coords
            
            # Connecter au nœud du réseau le plus proche
            self._connect_to_nearest_network_node(node_id, coords, max_distance=100.0)
        
        logger.info(f"{len(buildings_gdf)} bâtiments ajoutés au graphe")
    
    def _connect_to_nearest_network_node(self, node_id: str, coords: Tuple[float, float], max_distance: float = 50.0):
        """
        Connecte un nœud au nœud du réseau le plus proche.
        
        Args:
            node_id: ID du nœud à connecter
            coords: Coordonnées du nœud
            max_distance: Distance maximale de connexion
        """
        # Trouver les nœuds du réseau
        network_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'network']
        
        if not network_nodes:
            return
        
        # Calculer la distance au plus proche
        min_distance = float('inf')
        nearest_node = None
        
        for net_node in network_nodes:
            net_coords = self.node_positions.get(net_node, net_node)
            distance = ((coords[0] - net_coords[0])**2 + (coords[1] - net_coords[1])**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_node = net_node
        
        # Ajouter la connexion si dans la distance maximale
        if nearest_node and min_distance <= max_distance:
            self.graph.add_edge(node_id, nearest_node, 
                              length=min_distance, 
                              weight=min_distance,
                              type='connection')
    
    def find_shortest_path(self, source: str, target: str, weight: str = 'weight') -> List:
        """
        Trouve le plus court chemin entre deux nœuds.
        
        Args:
            source: Nœud source
            target: Nœud cible
            weight: Attribut à utiliser comme poids
            
        Returns:
            Liste de nœuds formant le chemin
        """
        try:
            path = nx.shortest_path(self.graph, source, target, weight=weight)
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"Aucun chemin trouvé entre {source} et {target}")
            return []
    
    def calculate_path_cost(self, path: List, weight: str = 'weight') -> float:
        """
        Calcule le coût total d'un chemin.
        
        Args:
            path: Liste de nœuds formant le chemin
            weight: Attribut à utiliser comme poids
            
        Returns:
            Coût total du chemin
        """
        if len(path) < 2:
            return 0.0
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                total_cost += edge_data.get(weight, 0.0)
        
        return total_cost
    
    def find_all_paths_to_substations(self, building_node: str) -> Dict[str, Tuple[List, float]]:
        """
        Trouve tous les chemins d'un bâtiment vers les postes de transformation.
        
        Args:
            building_node: ID du nœud bâtiment
            
        Returns:
            Dictionnaire {substation_id: (path, cost)}
        """
        substations = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'substation']
        
        paths = {}
        for substation in substations:
            path = self.find_shortest_path(building_node, substation)
            if path:
                cost = self.calculate_path_cost(path)
                paths[substation] = (path, cost)
        
        return paths
    
    def calculate_network_statistics(self) -> Dict:
        """
        Calcule des statistiques sur le graphe du réseau.
        
        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'is_connected': nx.is_connected(self.graph),
            'number_of_components': nx.number_connected_components(self.graph),
        }
        
        # Compter les types de nœuds
        node_types = {}
        for _, attr in self.graph.nodes(data=True):
            node_type = attr.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        stats['node_types'] = node_types
        
        # Statistiques sur les degrés
        degrees = [d for n, d in self.graph.degree()]
        if degrees:
            stats['avg_degree'] = sum(degrees) / len(degrees)
            stats['max_degree'] = max(degrees)
            stats['min_degree'] = min(degrees)
        
        # Longueur totale du réseau
        total_length = sum(data.get('length', 0) for _, _, data in self.graph.edges(data=True))
        stats['total_network_length'] = total_length
        
        return stats
    
    def identify_critical_nodes(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Identifie les nœuds critiques du réseau (betweenness centrality).
        
        Args:
            top_n: Nombre de nœuds à retourner
            
        Returns:
            Liste de tuples (node_id, centrality_score)
        """
        logger.info("Calcul de la centralité des nœuds...")
        centrality = nx.betweenness_centrality(self.graph, weight='weight')
        
        # Trier par centralité
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_nodes[:top_n]
    
    def export_graph(self, output_path: str, format: str = 'gexf'):
        """
        Exporte le graphe dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format de sortie ('gexf', 'graphml', 'gml')
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'gexf':
            nx.write_gexf(self.graph, output_file)
        elif format == 'graphml':
            nx.write_graphml(self.graph, output_file)
        elif format == 'gml':
            nx.write_gml(self.graph, output_file)
        else:
            raise ValueError(f"Format {format} non supporté")
        
        logger.info(f"Graphe exporté vers {output_path}")
    
    def visualize_graph(self, output_path: Optional[str] = None, figsize: Tuple[int, int] = (12, 10)):
        """
        Visualise le graphe.
        
        Args:
            output_path: Chemin pour sauvegarder la figure (optionnel)
            figsize: Taille de la figure
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=figsize)
            
            # Utiliser les positions réelles si disponibles
            pos = self.node_positions if self.node_positions else nx.spring_layout(self.graph)
            
            # Séparer les nœuds par type
            network_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'network']
            building_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'building']
            substation_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'substation']
            
            # Dessiner les arêtes
            nx.draw_networkx_edges(self.graph, pos, alpha=0.3, ax=ax)
            
            # Dessiner les nœuds par type
            if network_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=network_nodes,
                                     node_color='gray', node_size=50, label='Réseau', ax=ax)
            if building_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=building_nodes,
                                     node_color='blue', node_size=100, label='Bâtiments', ax=ax)
            if substation_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=substation_nodes,
                                     node_color='red', node_size=200, label='Postes', ax=ax)
            
            plt.legend()
            plt.title("Graphe du Réseau Électrique")
            plt.axis('off')
            
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                logger.info(f"Visualisation sauvegardée vers {output_path}")
            else:
                plt.show()
            
            plt.close()
            
        except ImportError:
            logger.error("Matplotlib n'est pas installé. Impossible de visualiser le graphe.")


def main():
    """Fonction principale pour démonstration."""
    logger.info("=== Modélisation du Réseau Électrique en Graphe ===")
    logger.info("Cet outil permet de modéliser le réseau électrique comme un graphe")
    logger.info("pour calculer les chemins optimaux de raccordement.")
    logger.info("")
    logger.info("Usage:")
    logger.info("  from network_model import NetworkGraphModel")
    logger.info("  model = NetworkGraphModel()")
    logger.info("  graph = model.build_graph_from_geodataframes(network_gdf, buildings_gdf, substations_gdf)")
    logger.info("  stats = model.calculate_network_statistics()")


if __name__ == "__main__":
    main()
