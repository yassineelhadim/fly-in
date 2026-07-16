import classes
import graph
from typing import Tuple, List, Dict


class Scheduler:
    def __init__(self,
                 map_data: MapData,
                 paths: List[List[str]]) -> None:

        self.map_data = map_data
        self.paths = paths
        self.drones: List[int] = []
        # I have the zone name and how many drones occupied it
        self.zone_occupancy: Dict[str, int] = {}
        # (zone1, zone2) -> drones that used this connection this turn
        self.used_connections: Dict[Tuple[str, str], int] = {}
        self.turn: int = 0

    def create_drones(self) -> None:
        nb_drones = self.map_data.nb_drones
        zones = self.map_data.zones
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                start_zone = zone
                break
        for i in range(nb_drones):
            self.drones.append(Drone([start_zone], i))

    def initialize_simulation(self):
        self.create_drones()
        

    def choose_path(self, drone):
        pass

    def can_move(self, drone, next_zone):
        pass

    def move_drone(self, drone):
        pass

    def process_turn(self):
        pass

    def simulation_finished(self):
        pass

    def run(self):
        pass