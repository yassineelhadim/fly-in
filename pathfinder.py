from typing import Dict, List, Optional, Tuple, Any
from heapq import heappush, heappop
from parser import MapData, Zone, start
from graph import Graph
import math

class Tracking_Data:
    """All the Data needed to implement Dijkstra algorithm"""
    def _init_(self, current, neighbors: List[str], distance: Dict[str, float], previous: Dict[str, None|Zone]) -> None:
        self.current = current
        self.neighbors = neighbors
        self.distance = distance
        self.previous = previous

class PathFinder:
    """Finds the shortest paths on the drone network using Dijkstra"""

    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.graph: Graph = Graph(map_data)
        self.visited_zones: List[str] = []
        self.previous: Dict[str, str] = {}

    def is_blocked(self, zone_name: Zone) -> bool:
        """Checks if a zone is blocked or not"""
        zone_object = self.map_data.zones[zone_name]
        zone_type = zone_object.zone_type
        if zone_type == "blocked":
            return True
        return False

    def is_priority(self, zone_name: Zone) -> bool:
        """Checks if a zone is a priority or not"""
        zone_object = self.map_data.zones[zone_name]
        zone_type = zone_object.zone_type
        if zone_type == "priority":
            return True
        return False

    def is_visited(self, current: Zone) -> bool:
        if current in self.visited_zones:
            return True
        return False

    def set_data(self, current: Zone | None) -> Tracking_Data:
        distance: Dict[str, float] = {}
        zones: Zone = self.map_data.zones
        if current is None:
            current: Zone = self.map_data.zones["start_hub"]
        previous: Dict[str, None|Zone] = {}
        neighbors = self.graph.get_neighbors(current)
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                distance["start"] = 0.00
                previous["start"] = None
            else:
                distance[zone] = math.inf
                previous[zone] = None
        # print(distance)
        # print(previous)
        return Tracking_Data(current, neighbors, distance, previous)


    def get_cl_zone(self) -> Zone:
        tracked = self.set_data()
        for neighbor in tracked.neighbors:
            zone_type = self.map_data.zones[neighbor].zone_type
            if zone_type == "normal" or zone_type == "priority":
                tracked.distance[neighbor] = 1
            elif zone_type == "restricted":
                tracked.distance[neighbor] = 2
        # find from distance the smallest zones in a sorted list
        # choose form the sorted list the smallest one that is unvisited
            


if __name__ == "__main__":
    data = start("/home/linux_yassine/42_cursus/fly-in/maps/easy/01_linear_path.txt")
    got_it = PathFinder(data)
    got_it.set_data(data)