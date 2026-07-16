from typing import Dict, List, Optional, Tuple, Any, Set
from parser import MapData, Zone, start
from graph import Graph, GraphEditor
import math


class PathFinder:
    """Finds the shortest paths on the drone network using Dijkstra"""

    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.graph: Graph = Graph(map_data)
        self.graph_editor: GraphEditor = GraphEditor(self.graph)
        self.visited_zones: Set[str] = set()
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

    def init_dis_a_pre(self) -> Tuple[Dict, Dict]:
        distance = {}
        previous = {}
        zones = self.map_data.zones
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                distance[zone] = 0.00
            else:
                distance[zone] = math.inf
            previous[zone] = None
        return (distance, previous)

    def update_neighbors(self, current: str, neighbors: List[str]) -> None:
        for neighbor in neighbors:
            zone_type = self.map_data.zones[neighbor].zone_type
            if zone_type == "normal" or zone_type == "priority":
                cost = 1
            elif zone_type == "restricted":
                cost = 2
            elif zone_type == "blocked":
                continue
            new_distance = self.distance[current] + cost
            if new_distance < self.distance[neighbor]:
                self.distance[neighbor] = new_distance
                self.previous[neighbor] = current

    def get_cl_zone(self) -> str | None:
        targeted_zones = []
        for zone in self.distance:
            zone_state = self.map_data.zones[zone].zone_type
            if not self.is_visited(zone) and zone_state != "blocked":
                targeted_zones.append(zone)
        if not targeted_zones:
            return None
        closest_zone = min(targeted_zones, key=self.distance.get)
        return self.map_data.zones[closest_zone].name

    def constructs_path(self) -> List[str]:
        for zone in self.map_data.zones:
            if self.map_data.zones[zone].zone_place == "end_hub":
                end_zone_name = zone
                break
        if self.distance[end_zone_name] == math.inf:
            return []
        tracking_list = []
        current = "end_hub"
        zone_name = end_zone_name
        while current != "start_hub":
            tracking_list.append(zone_name)
            zone_name = self.previous[zone_name]
            current = self.map_data.zones[zone_name].zone_place
            # I need to change current and the I need to update the zone name
            # the order might be the opposite
        tracking_list.append(zone_name)
        # I need to add the start node
        tracking_list.reverse()
        return tracking_list


    def dijkstra(self) -> list[str]:
        zones = self.map_data.zones
        for zone in zones:
            if zones[zone].zone_place == "start_hub":
                current_place = "start"
                current_zone = zones[zone].name
        nb_zones = len(zones)
        while len(self.visited_zones) < nb_zones:
            self.visited_zones.add(current_zone)
            neighbors = [x for x in self.graph.get_neighbors(current_zone) 
                         if not self.is_visited(x)]
            self.update_neighbors(current_zone, neighbors)
            closest_zone = self.get_cl_zone()
            if closest_zone is None or self.distance[closest_zone] == math.inf:
                break
            current_zone = closest_zone
        return self.constructs_path()

def find_multiple_paths(self) -> List[List[str]]:
    """Finds multiple valid paths by temporarily removing one connection."""
    paths = []
    # Find the shortest path
    first_path = self.dijkstra()
    if not first_path:
        return paths
    paths.append(first_path)
    # Try removing each connection in the shortest path
    for i in range(len(first_path) - 1):
        zone1 = first_path[i]
        zone2 = first_path[i + 1]
        self.graph_editor.remove_connection(zone1, zone2)
        # Reset Dijkstra's state
        self.visited_zones.clear()
        self.distance, self.previous = self.init_dis_a_pre()
        new_path = self.dijkstra()
        if new_path and new_path not in paths:
            paths.append(new_path)
        self.graph_editor.restore_connection(zone1, zone2)
    return paths



if __name__ == "__main__":
    map_data = start("/home/yel-hadi/fly-in/maps/easy/01_linear_path.txt")
    got_it = PathFinder(map_data)
    zones = got_it.map_data.zones
    for zone in zones:
        print(zone)