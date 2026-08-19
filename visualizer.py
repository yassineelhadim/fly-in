import time

from classes import Drone, MapData


class Visualizer:
    COLORS = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    RESET = "\033[0m"

    def __init__(self, delay: float = 0.4) -> None:
        self.delay = delay

    def show(
        self,
        map_data: MapData,
        drones: list[Drone],
        turn: int,
    ) -> None:
        counts: dict[str, int] = {}

        for drone in drones:
            position = drone.current_position
            counts[position] = counts.get(position, 0) + 1

        print("\033[2J\033[H", end="")
        print(f"Turn {turn}\n")

        for name, zone in map_data.zones.items():
            color = self.COLORS.get(
                zone.color or "white",
                self.COLORS["white"],
            )
            count = counts.get(name, 0)
            drones_str = "🛸 " * count

            print(
                f"  {color}{name:15s}{self.RESET} "
                f"{drones_str}({count})"
            )

        time.sleep(self.delay)
