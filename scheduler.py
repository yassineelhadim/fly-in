from typing import Dict, List, Tuple

from classes import Drone, MapData, ZoneType
from visualizer import Visualizer


class Scheduler:
    def __init__(
        self,
        map_data: MapData,
        paths: List[List[str]],
        visualize: bool = False,
    ) -> None:
        self.map_data = map_data
        self.paths = paths
        self.drones: List[Drone] = []
        self.zone_occupancy: Dict[str, int] = {}
        self.used_connections: Dict[Tuple[str, str], int] = {}
        self.turn: int = 0
        self.visualize_enabled = visualize
        self.visualizer = Visualizer()

        self.create_drones()
        self.initialize_simulation()

    def create_drones(self) -> None:
        nb_drones = self.map_data.nb_drones
        start_zone = self.map_data.start_zone

        for drone_id in range(nb_drones):
            self.drones.append(Drone([start_zone], drone_id))

    def initialize_simulation(self) -> None:
        self.turn = 0
        self.zone_occupancy = {
            zone_name: 0 for zone_name in self.map_data.zones
        }
        self.zone_occupancy[self.map_data.start_zone] = len(self.drones)
        self.used_connections = {}
        self.turn_moves: List[str] = []

    def choose_path(self, drone: Drone) -> None:
        if len(drone.path) > 1:
            return

        if not self.paths:
            raise ValueError("No paths available.")

        shortest_path = min(self.paths, key=len)

        drone.path = shortest_path
        drone.current_position = shortest_path[0]
        drone.step = 0

    def move_drone(self, drone: Drone) -> None:
        current_zone = drone.current_position
        next_zone = drone.path[drone.step + 1]
        next_zone_obj = self.map_data.zones[next_zone]

        self.zone_occupancy[current_zone] -= 1
        self.zone_occupancy[next_zone] += 1

        if current_zone < next_zone:
            connection: Tuple[str, str] = (
                current_zone,
                next_zone,
            )
        else:
            connection = (
                next_zone,
                current_zone,
            )

        self.used_connections[connection] = (
            self.used_connections.get(connection, 0) + 1
        )

        drone.move_drone()

        if next_zone_obj.zone_type == ZoneType.RESTRICTED:
            drone.wait_turns = 1

        self.turn_moves.append(f"D{drone.id_}-{next_zone}")

    def simulation_finished(self) -> bool:
        for drone in self.drones:
            if drone.current_position != self.map_data.end_zone:
                return False

        return True

    def can_move(self, drone: Drone) -> bool:
        current_zone = drone.current_position

        if drone.wait_turns > 0:
            return False

        if current_zone == self.map_data.end_zone:
            return False

        if drone.step + 1 >= len(drone.path):
            return False

        next_zone = drone.path[drone.step + 1]
        next_zone_obj = self.map_data.zones[next_zone]

        if next_zone_obj.zone_type == ZoneType.BLOCKED:
            return False

        occupancy = self.zone_occupancy.get(next_zone, 0)

        if (
            next_zone != self.map_data.end_zone
            and occupancy >= next_zone_obj.max_drones
        ):
            return False

        matching_connection = None

        for connection in self.map_data.connections:
            same_direction = (
                connection.zone1 == current_zone
                and connection.zone2 == next_zone
            )
            reverse_direction = (
                connection.zone1 == next_zone
                and connection.zone2 == current_zone
            )

            if same_direction or reverse_direction:
                matching_connection = connection
                break

        if matching_connection is None:
            return False

        if current_zone < next_zone:
            connection_key: Tuple[str, str] = (
                current_zone,
                next_zone,
            )
        else:
            connection_key = (
                next_zone,
                current_zone,
            )

        used_count = self.used_connections.get(connection_key, 0)

        if used_count >= matching_connection.max_link_capacity:
            return False

        return True

    def process_turn(self) -> None:
        self.turn_moves = []

        for drone in self.drones:
            if drone.wait_turns > 0:
                drone.wait_turns -= 1
                continue

            if len(drone.path) <= 1:
                self.choose_path(drone)

            if self.can_move(drone):
                self.move_drone(drone)

        if self.turn_moves:
            moves = " ".join(self.turn_moves)
            print(f"Turn {self.turn + 1}: {moves}")

        self.turn += 1

    def run(self) -> None:
        while not self.simulation_finished():
            self.used_connections = {}
            self.process_turn()

            if self.visualize_enabled:
                self.visualizer.show(
                    self.map_data,
                    self.drones,
                    self.turn,
                )

        print(f"Total turns: {self.turn}")
