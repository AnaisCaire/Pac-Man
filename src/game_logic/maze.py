from .config import LevelMazeSize
from mazegenerator.mazegenerator import MazeGenerator

WALL_BITS = {'N': 1, 'E': 2, 'S': 4, 'W': 8}

class Maze():
    """ Maze wrapper class """

    def __init__(self,
                 maze_size: LevelMazeSize,
                 seed: int):
        self.maze = MazeGenerator(size=(maze_size.width, maze_size.height),
                             seed=seed,
                             perfect=False)
        self.grid = self.maze.maze

    def has_wall(self, x: int, y: int, direction: str) -> bool:
        """ Returns True if there is a wall
        in the given direction (N/E/S/W) """
        return (self.grid[y][x] & WALL_BITS[direction]) != 0

    def is_wall(self, x: int, y: int) -> bool:
        """ Returns True if the cell is completely
        impassable (value 15, used for the '42' pattern) """
        return self.grid[y][x] == 15
