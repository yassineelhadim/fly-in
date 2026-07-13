from typing import List, Dict
from parser import MapData, Zone


class Graph:
    """Build the graph"""
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.adj: Dict[str, List[str]] = {}
        self._build_graph()

    def _build_graph(self) -> None:
        """Build adjacency list from connections (and skip blocked zones)"""
        for conn in self.map_data.connections:
            self.adj.setdefault(conn.zone1, []).append(conn.zone2)
            self.adj.setdefault(conn.zone2, []).append(conn.zone1)

    def get_neighbors(self, zone: str) -> List[str]:
        """Returns the neighbours of a specific Zone"""
        return self.adj.get(zone, [])


class GraphEditor:
    """Edits the graph and temporarily deletes one 
    connection so I can find multiple paths"""
    def __init__(self, original_graph: Graph) -> None:
        self.original_graph = original_graph

    def remove_connection(self, zone1: str, zone2: str) -> None:
        """Temporarily removes a connection between two zones."""
        if zone2 in self.original_graph.adj.get(zone1, []):
            self.original_graph.adj[zone1].remove(zone2)

        if zone1 in self.original_graph.adj.get(zone2, []):
            self.original_graph.adj[zone2].remove(zone1)

    def restore_connection(self, zone1: str, zone2: str) -> None:
        """Restores a previously removed connection."""
        if zone2 not in self.original_graph.adj.get(zone1, []):
            self.original_graph.adj[zone1].append(zone2)

        if zone1 not in self.original_graph.adj.get(zone2, []):
            self.original_graph.adj[zone2].append(zone1)

