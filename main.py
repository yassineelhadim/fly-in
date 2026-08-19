import sys

from parser import start
from pathfinder import PathFinder
from scheduler import Scheduler


def main():
    if len(sys.argv) != 2:
        print("Command line: python3 main.py <map_file>")
        sys.exit(1)
    map_file = sys.argv[1]
    try:
        map_data = start(map_file)
        path_finder = PathFinder(map_data)
        paths = path_finder.find_multiple_paths()
        if not paths:
            raise ValueError("No valid path found from start_hub to end_hub.")
        # Always enable visualization by default
        scheduler = Scheduler(map_data, paths, visualize=True)
        scheduler.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
