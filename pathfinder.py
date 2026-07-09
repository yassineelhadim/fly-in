from typing import Dict, List, Optional, Tuple, Any
from heapq import heappush, heappop
from parser import MapData, Zone, start
from graph import Graph
import math

class Tracking_Data():
    """All the Data needed to implement Dijkstra algorithm"""
    def __init__(self, current: Zone, neighbors: List[str], distance: Dict[str, float], previous: Dict[str, None|Zone]) -> None:
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
        self.previous: Dict[str, Zone | None] = self.init_dis_a_pre()[1]
        self.distance: Dict[str, float] = self.init_dis_a_pre()[0]

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

    def init_dis_a_pre(self) -> List[Dict, Dict]:
        distance = {}
        previous = {}
        zones = self.map_data.zones
        current = self.map_data.zones["start_hub"]
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start":
                distance[zone] = 0.00
            else:
                distance[zone] = math.inf
            previous[zone] = None
        return [distance, previous]


    def get_cl_zone(self, current: Zone) -> Zone:
        tracked = self.set_data(current)
        for neighbor in tracked.neighbors:
            zone_type = self.map_data.zones[neighbor].zone_type
            if zone_type == "normal" or zone_type == "priority":
                tracked.distance[neighbor] = 1
            elif zone_type == "restricted":
                tracked.distance[neighbor] = 2
        unvisited_zones = {}
        for zone in tracked.distance:
            if not self.is_visited(zone):
                unvisited_zones[zone] = tracked.distance[zone]
        closest_zone = min(unvisited_zones, key=unvisited_zones.get)
        return map_data.zones[closest_zone]

    def dijkstra(self):
        cur_zone = self.map_data.zones[]
        closest = self.get_cl_zone()


if __name__ == "__main__":
    map_data = start("/home/yel-hadi/fly-in/maps/easy/01_linear_path.txt")
    got_it = PathFinder(map_data)

    zones = map_data.zones
    for zone in zones:
        print(f'The current zone is:{got_it.get_cl_zone(map_data.zones[zone])}\n')