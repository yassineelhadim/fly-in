import time

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


def show(map_data, drones, turn):
    counts = {}
    for d in drones:
        counts[d.current_position] = counts.get(d.current_position, 0) + 1

    print("\033[2J\033[H", end="")
    print(f"Turn {turn}\n")
    for name, zone in map_data.zones.items():
        c = COLORS.get(zone.color, COLORS["white"])
        n = counts.get(name, 0)
        drones_str = "🛸 " * n
        print(f"  {c}{name:15s}{RESET} {drones_str}({n})")
    time.sleep(0.4)
