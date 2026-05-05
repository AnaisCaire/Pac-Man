from src import parse_config
from src import game_loop
import sys

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 a_maze_ing.py config.txt\n")
        sys.exit(1)

    config = parse_config(sys.argv[1])
    game_loop(config)

main()
