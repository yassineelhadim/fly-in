from classes import Zone, ZoneType, MapData, Connection


class Parser:
    """Parses a drone network map file into a MapData object."""

    def _is_valid_color(self, color: str) -> bool:
        """Check if a color value is valid."""
        return bool(color) and " " not in color and "\t" not in color

    def __init__(self, filepath: str) -> None:
        """Initialize Parser with a file path."""
        self.filepath: str = filepath

    def _parse_nb_drones(self, line: str, line_index: int) -> int:
        """Parse the nb_drones line and return the drone count."""
        line_parts = line.split("#", 1)
        line = line_parts[0].strip()

        parts = line.split(":")
        if len(parts) != 2:
            raise ValueError(f"Line {line_index}: Invalid nb_drones format.")

        nb_value = parts[1].strip()
        msg1 = f"Line {line_index}"
        msg = msg1 + ": nb_drones value should be a positive integer."
        if not nb_value.isdigit() or int(nb_value) <= 0:
            raise ValueError(
                msg
            )

        nb_drones_val = int(nb_value)
        msg = f"Line {line_index}: nb_drones value exceeds maximum of 10,000."
        if nb_drones_val > 10000:
            raise ValueError(
                msg
            )

        return nb_drones_val

    def _parse_zone(
        self, line: str, line_index: int, drone_prefix: str
    ) -> Zone:
        """Parse a zone line and return a Zone object."""
        line_parts = line.split("#", 1)
        line_content = line_parts[0].strip()

        rest = line_content[len(drone_prefix) + 1:].strip()
        metadata: dict[str, str] = {}
        last_bracket_start = rest.rfind("[")
        last_bracket_end = rest.rfind("]")

        if (
            last_bracket_start != -1
            and last_bracket_end != -1
            and last_bracket_start < last_bracket_end
        ):
            after_bracket = rest[last_bracket_end + 1:].strip()
            if after_bracket:
                raise ValueError(
                    f'Line {line_index}: Unexpected content after closing '
                    f'bracket: "{after_bracket}".'
                )

            if "=" in rest[last_bracket_start + 1:last_bracket_end]:
                metadata = self._parse_metadata(
                    rest[last_bracket_start + 1:last_bracket_end],
                    line_index,
                    drone_prefix,
                )
                rest = rest[:last_bracket_start].strip()
            else:
                raise ValueError(
                    f"Line {line_index}: Invalid metadata format in brackets."
                )
        elif last_bracket_start != -1 or last_bracket_end != -1:
            raise ValueError(f"Line {line_index}: zone must have name x y.")

        parts = rest.split()
        if len(parts) != 3:
            raise ValueError(f"Line {line_index}: zone must have name x y.")

        name = parts[0]

        if drone_prefix == "start_hub":
            zone_place = "start_hub"
        elif drone_prefix == "end_hub":
            zone_place = "end_hub"
        else:
            zone_place = "hub"

        if "-" in name:
            raise ValueError(f'Line {line_index}: name contains "-".')

        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError(
                f"Line {line_index}: coordinates must be integers."
            )

        z_type_str = metadata.get("zone", "normal")

        if (
            drone_prefix in ("start_hub", "end_hub")
            and z_type_str == "blocked"
        ):
            raise ValueError(
                f"Line {line_index}: {drone_prefix} cannot have zone=blocked."
            )

        color = metadata.get("color")

        try:
            max_d = int(metadata.get("max_drones", "1"))
            if max_d <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                f"Line {line_index}: max_drones must be a positive integer."
            )

        valid_types = {zt.value: zt for zt in ZoneType}

        if z_type_str not in valid_types:
            raise ValueError(
                f'Line {line_index}: The zone type "{z_type_str}" is invalid.'
            )

        z_type = valid_types[z_type_str]

        if color is not None and not self._is_valid_color(color):
            raise ValueError(
                f'Line {line_index}: "{color}" is not a valid color.'
            )

        return Zone(
            name,
            x,
            y,
            z_type,
            color,
            max_d,
            zone_place,
        )

    def _parse_connection(
        self, line: str, line_index: int
    ) -> Connection:
        """Parse a connection line and return a Connection object."""
        line_parts = line.split("#", 1)
        line_content = line_parts[0].strip()

        rest = line_content[len("connection:"):].strip()
        metadata: dict[str, str] = {}
        last_bracket_start = rest.rfind("[")
        last_bracket_end = rest.rfind("]")

        if (
            last_bracket_start != -1
            and last_bracket_end != -1
            and last_bracket_start < last_bracket_end
        ):
            after_bracket = rest[last_bracket_end + 1:].strip()

            if after_bracket:
                raise ValueError(
                    f'Line {line_index}: Unexpected content after closing '
                    f'bracket: "{after_bracket}".'
                )

            if "=" in rest[last_bracket_start + 1:last_bracket_end]:
                metadata = self._parse_metadata(
                    rest[last_bracket_start + 1:last_bracket_end],
                    line_index,
                    "connection",
                )
                rest = rest[:last_bracket_start].strip()
            else:
                raise ValueError(
                    f"Line {line_index}: Invalid metadata format in brackets."
                )
        elif last_bracket_start != -1 or last_bracket_end != -1:
            raise ValueError(
                f'Line {line_index}: connection syntax must be '
                f'"name1-name2".'
            )

        parts = rest.split("-")

        if len(parts) != 2:
            raise ValueError(
                f'Line {line_index}: connection syntax must be '
                f'"name1-name2".'
            )

        zn1 = parts[0].strip()
        zn2 = parts[1].strip()
        msg = f'Line {line_index}: Self-connection "{zn1}-{zn2}" not allowed.'
        if zn1 == zn2:
            raise ValueError(
                msg
            )

        if not zn1 or not zn2:
            raise ValueError(
                f"Line {line_index}: Connection pair cannot have "
                f"empty zone names."
            )

        try:
            mlc = int(metadata.get("max_link_capacity", "1"))
            if mlc <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                f"Line {line_index}: max_link_capacity must be "
                f"a positive integer."
            )

        return Connection(zn1, zn2, mlc)

    def _parse_metadata(
        self,
        metadata_str: str,
        line_index: int,
        entity_type: str = "zone",
    ) -> dict[str, str]:
        """Parse a metadata block."""
        result: dict[str, str] = {}

        cleaned_metadata_str = metadata_str.replace(",", " ")

        for part in cleaned_metadata_str.strip().split():
            if "=" not in part:
                raise ValueError(
                    f"Line {line_index}: Invalid metadata '{part}'."
                )

            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(
                    f"Line {line_index}: Metadata key cannot be empty."
                )

            if key in result:
                raise ValueError(
                    f"Line {line_index}: Duplicate metadata key '{key}'."
                )

            result[key] = value

        if entity_type in ["start_hub", "end_hub", "hub"]:
            allowed_keys = {"zone", "color", "max_drones"}

            for key in result.keys():
                if key not in allowed_keys:
                    raise ValueError(
                        f"Line {line_index}: Invalid metadata key '{key}' "
                        f"for {entity_type}. Allowed keys: "
                        f"{', '.join(sorted(allowed_keys))}."
                    )

        elif entity_type == "connection":
            allowed_keys = {"zone", "max_link_capacity"}

            for key in result.keys():
                if key not in allowed_keys:
                    raise ValueError(
                        f"Line {line_index}: Invalid metadata key '{key}' "
                        f"for connection. Allowed keys: "
                        f"{', '.join(sorted(allowed_keys))}."
                    )

        return result

    def parse(self) -> MapData:
        """Read the file and parse it into a MapData object."""
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
            raise FileNotFoundError(
                f'Error: the File "{self.filepath}" was not found.'
            )

        for line_index, line_text in enumerate(lines, start=1):
            line = line_text.strip()

            if not line or line.startswith("#"):
                continue

            if not nb_drones_found:
                if not line.startswith("nb_drones:"):
                    raise ValueError(
                        f"Line {line_index}: First line must be nb_drones."
                    )

                nb_drones = self._parse_nb_drones(line, line_index)
                nb_drones_found = True

            elif line.startswith("start_hub:"):
                if start_found:
                    raise ValueError(
                        f"Line {line_index}: Only one start_hub is allowed."
                    )

                zone = self._parse_zone(
                    line, line_index, "start_hub"
                )

                if zone.name in zones:
                    raise ValueError(
                        f"Line {line_index}: Duplicate zone name "
                        f"'{zone.name}'."
                    )

                zones[zone.name] = zone
                start_zone = zone.name
                start_found = True

            elif line.startswith("end_hub:"):
                if end_found:
                    raise ValueError(
                        f"Line {line_index}: Only one end_hub is allowed."
                    )

                zone = self._parse_zone(
                    line, line_index, "end_hub"
                )

                if zone.name in zones:
                    raise ValueError(
                        f"Line {line_index}: Duplicate zone name "
                        f"'{zone.name}'."
                    )

                zones[zone.name] = zone
                end_zone = zone.name
                end_found = True

            elif line.startswith("hub:"):
                zone = self._parse_zone(
                    line, line_index, "hub"
                )

                if zone.name in zones:
                    raise ValueError(
                        f"Line {line_index}: Duplicate zone name "
                        f"'{zone.name}'."
                    )

                zones[zone.name] = zone

            elif line.startswith("connection:"):
                con = self._parse_connection(line, line_index)

                if con.zone1 not in zones:
                    raise ValueError(
                        f"Line {line_index}: Unknown zone '{con.zone1}'."
                    )

                if con.zone2 not in zones:
                    raise ValueError(
                        f"Line {line_index}: Unknown zone '{con.zone2}'."
                    )

                for existing in connections:
                    same_direction = (
                        existing.zone1 == con.zone1
                        and existing.zone2 == con.zone2
                    )
                    reverse_direction = (
                        existing.zone1 == con.zone2
                        and existing.zone2 == con.zone1
                    )

                    if same_direction or reverse_direction:
                        raise ValueError(
                            f'Line {line_index}: Duplicate connection '
                            f'"{con.zone1}-{con.zone2}".'
                        )

                connections.append(con)

            else:
                raise ValueError(
                    f"Line {line_index}: Unrecognized line format."
                )

        if not nb_drones_found:
            raise ValueError("Error: nb_drones is not defined.")

        if not start_found:
            raise ValueError("Error: No start_hub defined.")

        if not end_found:
            raise ValueError("Error: No end_hub defined.")

        return MapData(
            nb_drones,
            start_zone,
            end_zone,
            zones,
            connections,
        )


def start(file_path: str) -> MapData:
    """Initialize the parser and parse the given file."""
    try:
        map_data = Parser(file_path).parse()
        return map_data
    except (ValueError, FileNotFoundError) as e:
        raise ValueError(f"{e}")
