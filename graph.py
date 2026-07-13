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

