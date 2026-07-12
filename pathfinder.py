from typing import Dict, List, Optional, Tuple, Any
from heapq import heappush, heappop
from parser import MapData, Zone, start
from graph import Graph
import math


class PathFinder:
    """Finds the shortest paths on the drone network using Dijkstra"""

    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.graph: Graph = Graph(map_data)
        self.visited_zones: List[str] = []
        self.distance, self.previous = self.init_dis_a_pre()[0]

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

    def update_neighbors(self, current: Zone) -> None:
        neighbors = self.graph.get_neighbors(current)
        for neighbor in neighbors:
            zone_type = self.map_data.zones[neighbor].zone_type
            if zone_type == "normal" or zone_type == "priority":
                self.distance[neighbor] = 1
            elif zone_type == "restricted":
                self.distance[neighbor] = 2

    def get_cl_zone(self, current: Zone) -> Zone:
        # ------this is for updating the distance, I will do it in another function-------------
        # neighbors = self.graph.get_neighbors(current)
        # for neighbor in neighbors:
        #     zone_type = self.map_data.zones[neighbor].zone_type
        #     if zone_type == "normal" or zone_type == "priority":
        #         self.distance[neighbor] = 1
        #     elif zone_type == "restricted":
        #         self.distance[neighbor] = 2
        unvisited_zones = {}
        for zone in self.distance:
            if not self.is_visited(zone):
                unvisited_zones[zone] = self.distance[zone]
        closest_zone = min(unvisited_zones, key=unvisited_zones.get)
        return map_data.zones[closest_zone]

    def dijkstra(self):
        zones = self.map_data.zones
        for zone in zones:
            if zones[zone].zone_place == "start":
                current_place = "start"
                current_zone = zones[zone].name
        nb_zones = len(zones)
        while len(self.visited_zones) < nb_zones:
            closest_zone = self.get_cl_zone(current_zone)
            self.visited_zones.append(closest_zone)
            
            


if __name__ == "__main__":
    map_data = start("/home/yel-hadi/fly-in/maps/easy/01_linear_path.txt")
    got_it = PathFinder(map_data)