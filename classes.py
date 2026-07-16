from enum import Enum
from typing import List, Dict, Tuple


class ZoneType(Enum):
    """Represents the type of a zone in the drone network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone():
    """Represents a single zone (node) in the drone network."""

    def __init__(self,
                 name: str,
                 x: int,
                 y: int,
                 zone_type: ZoneType,
                 color: str | None,
                 max_drones: int,
                 zone_place: str
                 ) -> None:
        """Initialize a Zone.

        Args:
            name: Unique zone identifier.
            x: X coordinate.
            y: Y coordinate.
            zone_type: Type of zone (normal, blocked, etc).
            color: Optional display color.
            max_drones: Max drones allowed simultaneously.
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneType = zone_type
        self.color: str | None = color
        self.max_drones: int = max_drones
        self.zone_place: str = zone_place


class Connection():
    """Represents a bidirectional connection (edge) between two zones."""

    def __init__(self, zone1: str, zone2: str, max_link_capacity: int) -> None:
        """Initialize a Connection.

        Args:
            zone1: Name of the first zone.
            zone2: Name of the second zone.
            max_link_capacity: Max drones traversing simultaneously.
        """
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity


class MapData():
    """Holds all data extracted from a parsed map file."""

    def __init__(self,
                 nb_drones: int,
                 start_zone: str,
                 end_zone: str,
                 zones: dict[str, Zone],
                 connections: list[Connection]
                 ) -> None:
        """Initialize MapData.

        Args:
            nb_drones: Total number of drones.
            start_zone: Name of the starting zone.
            end_zone: Name of the ending zone.
            zones: Dictionary of zone name to Zone object.
            connections: List of all connections.
        """
        self.nb_drones: int = nb_drones
        self.start_zone: str = start_zone
        self.end_zone: str = end_zone
        self.zones: dict[str, Zone] = zones
        self.connections: list[Connection] = connections

class Drone():
    def __init__(self, path: List[str], id_: int) -> None:
        self.path: List[str] = path
        self.id_: int = id_
        self.current_position: str = self.path[0]
        self.step: int = 0

    # def move_drone(self) -> None:
    #     self.step += 1
    #     self.current_position = self.path[self.step]