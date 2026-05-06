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
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        self.corners = [(0, 0),
                    (self.width - 1, 0),
                    (0, self.height - 1),
                    (self.width - 1, self.height - 1)]

    def has_wall(self, x: int, y: int, direction: str) -> bool:
        """ Returns True if there is a wall
        in the given direction (N/E/S/W) """
        return (self.grid[y][x] & WALL_BITS[direction]) != 0

    def is_wall(self, x: int, y: int) -> bool:
        """ Returns True if the cell is completely
        impassable (value 15, used for the '42' pattern) """
        return self.grid[y][x] == 15
    
    def find_spawn(self) -> tuple[int, int]:
        """ 
        go to center then scan to find next valid cell
        manhattan technique: 
        1. for each radius check where cells == r
        2.abs(dx) + abs(dy) != r
        """
        cx, cy =  self.width // 2, self.height // 2
        for r in range(max( self.width,  self.height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:   # only the shell at distance r
                        continue
                    x, y = cx + dx, cy + dy
                    if 0 <= x <  self.width and 0 <= y <  self.height and not self.is_wall(x, y):
                        return (x, y)
        return (cx, cy)

    def place_pacgums(self, spawn: tuple[int, int]) -> set[tuple[int, int]]:
        pacgums: set[tuple[int, int]] = set()

        for y in range( self.height):
            for x in range( self.width):
                if (x, y) not in  self.corners and not self.is_wall(x, y) and (x, y) != spawn:
                    pacgums.add((x, y))
        return pacgums

    def place_super_pacgums(self) -> set[tuple[int, int]]:
        """ for the corners """
        super_pacgums: set[tuple[int, int]] = set()
        for (corner_x, corner_y) in self.corners:
            super_pacgums.add((corner_x, corner_y))
        return super_pacgums