
from src import parse_config
import sys

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 a_maze_ing.py config.txt\n")
        sys.exit(1)
    
    config_path = sys.argv[1]

    config = parse_config(config_path)
    print(config)
    return config

main()