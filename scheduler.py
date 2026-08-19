import classes
from typing import Tuple, List, Dict
from classes import MapData, Drone, ZoneType
from visualizer import show


class Scheduler:
    def __init__(
        self, map_data: MapData, paths: List[List[str]], visualize: bool = False
    ) -> None:

        self.map_data = map_data
        self.paths = paths
        self.drones: List[Drone] = []
        # I have the zone name and how many drones occupied it
        self.zone_occupancy: Dict[str, int] = {}
        # (zone1, zone2) -> drones that used this connection this turn
        self.used_connections: Dict[Tuple[str, str], int] = {}
        self.turn: int = 0
        self.visualize_enabled = visualize
        self.create_drones()
        self.initialize_simulation()

    def create_drones(self) -> None:
        nb_drones = self.map_data.nb_drones
        zones = self.map_data.zones
        for zone in zones:
            if self.map_data.zones[zone].zone_place == "start_hub":
                start_zone = zone
                break
        for i in range(nb_drones):
            self.drones.append(Drone([start_zone], i))

    def initialize_simulation(self) -> None:
        """Initialize the simulation state."""
        self.turn = 0
        # Number of drones currently inside each zone
        self.zone_occupancy: dict[str, int] = {}
        for zone_name in self.map_data.zones:
            self.zone_occupancy[zone_name] = 0
        # Initially every drone is inside the start hub
        self.zone_occupancy[self.map_data.start_zone] = len(self.drones)
        # Number of drones that used each connection this turn
        self.used_connections: dict[tuple[str, str], int] = {}
        # Moves performed during the current turn
        self.turn_moves: list[str] = []

    def choose_path(self, drone: Drone) -> None:
        """Assign the shortest available path to a drone."""

        # Drone already has a path
        if len(drone.path) > 1:
            return

        if not self.paths:
            raise ValueError("No paths available.")

        shortest_path = min(self.paths, key=len)

        drone.path = shortest_path
        drone.current_position = shortest_path[0]
        drone.step = 0

    def move_drone(self, drone: Drone) -> None:
        """Move a drone and update the simulation state."""

        current_zone = drone.current_position
        next_zone = drone.path[drone.step + 1]
        next_zone_obj = self.map_data.zones[next_zone]

        # Update zone occupancy
        self.zone_occupancy[current_zone] -= 1
        self.zone_occupancy[next_zone] += 1

        # Update connection usage
        connection = tuple(sorted((current_zone, next_zone)))

        if connection not in self.used_connections:
            self.used_connections[connection] = 0

        self.used_connections[connection] += 1

        # Move the drone
        drone.move_drone()

        # Restricted zones take an extra turn before the drone can leave them.
        if next_zone_obj.zone_type == ZoneType.RESTRICTED:
            drone.wait_turns = 1

        # Save move for printing later
        self.turn_moves.append(f"D{drone.id_}-{next_zone}")

    def simulation_finished(self) -> bool:
        """Returns True when every drone reached the end hub."""
        for drone in self.drones:
            if drone.current_position != self.map_data.end_zone:
                return False
        return True

    def can_move(self, drone: Drone) -> bool:
        current_zone = drone.current_position

        if drone.wait_turns > 0:
            return False

        # 1. Drone already at destination
        if current_zone == self.map_data.end_zone:
            return False

        # 2. No next zone in its assigned path
        if drone.step + 1 >= len(drone.path):
            return False

        # 3. Determine next zone
        next_zone = drone.path[drone.step + 1]

        # 4. Next zone blocked
        next_zone_obj = self.map_data.zones[next_zone]
        if next_zone_obj.zone_type == classes.ZoneType.BLOCKED:
            return False

        # 5. Destination zone full
        next_zone_occupancy = self.zone_occupancy.get(next_zone, 0)
        if (
            next_zone != self.map_data.end_zone
            and next_zone_occupancy >= next_zone_obj.max_drones
        ):
            return False

        # 6. Find the connection between current and next zones
        matching_connection = None
        for connection in self.map_data.connections:
            if (connection.zone1 == current_zone and connection.zone2 == next_zone) or (
                connection.zone1 == next_zone and connection.zone2 == current_zone
            ):
                matching_connection = connection
                break

        if matching_connection is None:
            return False

        # 7. Link capacity reached for this turn
        connection_key = tuple(sorted((current_zone, next_zone)))
        used_count = self.used_connections.get(connection_key, 0)
        if used_count >= matching_connection.max_link_capacity:
            return False

        # 8. All checks passed
        return True

    def process_turn(self) -> None:
        # 1. Clear this turn's move list.
        self.turn_moves = []

        # 2. Process each drone.
        for drone in self.drones:
            if drone.wait_turns > 0:
                drone.wait_turns -= 1
                continue

            if len(drone.path) <= 1:
                self.choose_path(drone)

            if self.can_move(drone):
                self.move_drone(drone)

        # 3. Print only turns where at least one drone moved.
        if self.turn_moves:
            print(f"Turn {self.turn + 1}: {' '.join(self.turn_moves)}")

        # 4. Increase the turn counter.
        self.turn += 1

    def run(self) -> None:
        while not self.simulation_finished():
            self.used_connections = {}
            self.process_turn()
            if self.visualize_enabled:
                show(self.map_data, self.drones, self.turn)
        print(f"Total turns: {self.turn}")
