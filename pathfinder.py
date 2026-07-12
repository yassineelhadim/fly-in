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
        self.distance, self.previous = self.init_dis_a_pre()

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

    def init_dis_a_pre(self) -> List[Dict]:
        distance = {}
        previous = {}
        zones = self.map_data.zones
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                current = zone
        current = self.map_data.zones["start"]
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                distance[zone] = 0.00
            else:
                distance[zone] = math.inf
            previous[zone] = None
        return [distance, previous]

    def update_neighbors(self, current: Zone, neighbors: List[str]) -> None:
        for neighbor in neighbors:
            zone_type = self.map_data.zones[neighbor].zone_type
            if zone_type == "normal" or zone_type == "priority":
                cost = 1
            elif zone_type == "restricted":
                cost = 2
            new_distance = self.distance[current.name] + cost
            if new_distance < self.distance[neighbor]:
                self.distance[neighbor] = new_distance
                self.previous[neighbor] = current.name

    def get_cl_zone(self) -> Zone:
        # I need to check the cost of the neighbors and choose the closest one
        targeted_zones = []
        for zone in self.distance:
            zone_state = self.map_data.zones[zone].zone_type
            if not self.is_visited(zone) and zone_state != "blocked":
                targeted_zones.append(zone)
        closest_zone = min(targeted_zones, key=self.distance.get)
        return self.map_data.zones[closest_zone].name

    def dijkstra(self):
        zones = self.map_data.zones
        for zone in zones:
            if zones[zone].zone_place == "start":
                current_place = "start"
                current_zone = zones[zone].name
        nb_zones = len(zones)
        while len(self.visited_zones) < nb_zones:
            self.visited_zones.append(current_zone)
            neighbors = self.graph.get_neighbors(current_zone)
            # currently checking if I am getting the cl_zone correctly
            closest_zone = self.get_cl_zone(current_zone, neighbors)
            self.visited_zones.append(closest_zone)
            
            


if __name__ == "__main__":
    map_data = start("/home/yel-hadi/fly-in/maps/easy/01_linear_path.txt")
    got_it = PathFinder(map_data)
    zones = got_it.map_data.zones
    for zone in zones:
        print(zone)