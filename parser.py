import sys
import re
try:
    import pygame  # type: ignore
except ModuleNotFoundError:
    pygame = None
from classes import Zone, ZoneType, MapData, Connection


class Parser():
    """Parses a drone network map file into a MapData object."""

    FALLBACK_COLOR_NAMES = {
        "black", "silver", "gray", "white", "maroon", "red", "purple",
        "fuchsia", "green", "lime", "olive", "yellow", "navy", "blue",
        "teal", "aqua", "orange", "pink", "brown", "cyan", "magenta",
    }

    def _is_valid_color(self, color: str) -> bool:
        if pygame is not None:
            pygame.init()
            return color in pygame.color.THECOLORS
        if color in self.FALLBACK_COLOR_NAMES:
            return True
        return re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", color) is not None

    def __init__(self, filepath: str) -> None:
        """Initialize Parser with a file path.

        Args:
            filepath: Path to the map file.
        """
        self.filepath: str = filepath

    def _parse_nb_drones(self, line: str, line_index: int) -> int:
        """Parse the nb_drones line and return the drone count.

        Args:
            line: The raw line from the file.
            line_index: Line number for error reporting.

        Returns:
            Number of drones as a positive integer.
        """
        parts = line.split(":")
        if len(parts) != 2:
            raise ValueError(f"Line {line_index}: Invalid nb_drones format.")
        nb_value = parts[1].strip()
        if not nb_value.isdigit() or int(nb_value) <= 0:
            raise ValueError(f"Line {line_index}: nb_drones value should be a positive integer.")
        return int(nb_value)

    def _parse_zone(self, line: str, line_index: int, drone_prefix: str) -> Zone:
        """Parse a zone line and return a Zone object.

        Args:
            line: The raw line from the file.
            line_index: Line number for error reporting.
            drone_prefix: One of 'start_hub', 'end_hub', 'hub'.

        Returns:
            A Zone object.
        """
        rest = line[len(drone_prefix) + 1:].strip()
        metadata: dict[str, str] = {}
        if "[" in rest and "]" in rest:
            m_start = rest.index("[")
            m_end = rest.index("]")
            metadata = self._parse_metadata(rest[m_start + 1:m_end], line_index)
            rest = rest[:m_start]
        parts = rest.split()
        if len(parts) != 3:
            raise ValueError(f"Line {line_index}: zone must have name x y.")
        name = parts[0]
        if drone_prefix == "start_hub":
            zone_place = "start_hub"
        elif drone_prefix == "end_hub":
            zone_place = "end_hub"
        elif drone_prefix == "hub":
            zone_place = "hub"
        i = 0
        if "-" in name:
            raise ValueError(f'Line {line_index}: name contains "-".')
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError(f"Line {line_index}: coordinates must be integers.")
        z_type_str = metadata.get("zone", "normal")
        color = metadata.get("color", None)
        try:
            max_d = int(metadata.get("max_drones", "1"))
            if max_d <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(f'Line {line_index}: max_drones must be a positive integer.')
        valid_types = {zt.value: zt for zt in ZoneType}
        if z_type_str not in valid_types:
            raise ValueError(f'Line {line_index}: The zone type "{z_type_str}" is invalid.')
        z_type = valid_types[z_type_str]
        if color is not None and not self._is_valid_color(color):
            raise ValueError(f'Line {line_index}: "{color}" is not a valid color.')
        return Zone(name, x, y, z_type, color, max_d, zone_place)

    def _parse_connection(self, line: str, line_index: int) -> Connection:
        """Parse a connection line and return a Connection object.

        Args:
            line: The raw line from the file.
            line_index: Line number for error reporting.

        Returns:
            A Connection object.
        """
        rest = line[len("connection:"):].strip()
        metadata: dict[str, str] = {}
        if "[" in rest and "]" in rest:
            i_start = rest.index("[")
            i_end = rest.index("]")
            metadata = self._parse_metadata(rest[i_start + 1:i_end], line_index)
            rest = rest[:i_start].strip()
        parts = rest.split("-")
        if len(parts) != 2:
            raise ValueError(f'Line {line_index}: connection syntax must be "name1-name2".')
        zn1 = parts[0].strip()
        zn2 = parts[1].strip()
        try:
            mlc = int(metadata.get("max_link_capacity", "1"))
            if mlc <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(f'Line {line_index}: max_link_capacity must be a positive integer.')
        return Connection(zn1, zn2, mlc)

    def _parse_metadata(self, metadata_str: str, line_index: int) -> dict[str, str]:
        """Parse a metadata block like zone=restricted color=red max_drones=2.

        Args:
            metadata_str: The content inside the brackets.
            line_index: Line number for error reporting.

        Returns:
            Dictionary of key-value pairs from the metadata.
        """
        result: dict[str, str] = {}
        for part in metadata_str.strip().split():
            if "=" not in part:
                raise ValueError(f"Line {line_index}: Invalid metadata '{part}'.")
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
        return result

    def parse(self) -> MapData:
        """Read the file and parse it into a MapData object.

        Returns:
            A fully populated MapData object.
        """
        nb_drones: int = 0
        start_zone: str = ""
        end_zone: str = ""
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        nb_drones_found = False
        start_found = False
        end_found = False

        try:
            with open(self.filepath, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f'Error: the File "{self.filepath}" was not found.')

        for line_index, line_text in enumerate(lines, start=1):
            line = line_text.strip()
            if not line or line.startswith("#"):
                continue
            if not nb_drones_found:
                if not line.startswith("nb_drones:"):
                    raise ValueError(f"Line {line_index}: First line must be nb_drones.")
                nb_drones = self._parse_nb_drones(line, line_index)
                nb_drones_found = True
            elif line.startswith("start_hub:"):
                if start_found:
                    raise ValueError(f"Line {line_index}: Only one start_hub is allowed.")
                zone: Zone = self._parse_zone(line, line_index, "start_hub")
                if zone.name in zones:
                    raise ValueError(f"Line {line_index}: Duplicate zone name '{zone.name}'.")
                zones[zone.name] = zone
                start_zone = zone.name
                start_found = True
            elif line.startswith("end_hub:"):
                if end_found:
                    raise ValueError(f"Line {line_index}: Only one end_hub is allowed.")
                zone = self._parse_zone(line, line_index, "end_hub")
                if zone.name in zones:
                    raise ValueError(f"Line {line_index}: Duplicate zone name '{zone.name}'.")
                zones[zone.name] = zone
                end_zone = zone.name
                end_found = True
            elif line.startswith("hub:"):
                zone = self._parse_zone(line, line_index, "hub")
                if zone.name in zones:
                    raise ValueError(f"Line {line_index}: Duplicate zone name '{zone.name}'.")
                zones[zone.name] = zone
            elif line.startswith("connection:"):
                con = self._parse_connection(line, line_index)
                if con.zone1 not in zones:
                    raise ValueError(f"Line {line_index}: Unknown zone '{con.zone1}'.")
                if con.zone2 not in zones:
                    raise ValueError(f"Line {line_index}: Unknown zone '{con.zone2}'.")
                for existing in connections:
                    if (existing.zone1 == con.zone1 and existing.zone2 == con.zone2 or
                            existing.zone1 == con.zone2 and existing.zone2 == con.zone1):
                        raise ValueError(f'Line {line_index}: Duplicate connection "{con.zone1}-{con.zone2}".')
                connections.append(con)
            else:
                raise ValueError(f"Line {line_index}: Unrecognized line format.")

        if not nb_drones_found:
            raise ValueError("Error: nb_drones is not defined.")
        if not start_found:
            raise ValueError("Error: No start_hub defined.")
        if not end_found:
            raise ValueError("Error: No end_hub defined.")
        return MapData(nb_drones, start_zone, end_zone, zones, connections)


def start(file_path: str) -> MapData:
    """Initialize the parser and parse the given file.

    Args:
        file_path: Path to the map file.

    Returns:
        Parsed MapData object.
    """
    try:
        map_data = Parser(file_path).parse()
        return map_data
    except (ValueError, FileNotFoundError) as e:
        raise ValueError(f"{e}")
