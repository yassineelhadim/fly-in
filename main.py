import sys
from parser import start

def main():
    if len(sys.argv) != 2:
        print("Command line: python3 main.py <map_file>")
        sys.exit(1)
    filepath = sys.argv[1]
    try:
        with open(filepath, "r") as file_path:
            start(file_path)
    except Exception as e:
        print(f'Error: {e}')
    



if __name__ == "__main__":
    main()