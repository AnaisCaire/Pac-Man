from typing import Tuple
from .config import Config
from .maze import Maze

class Player:
    """
    Represents the player entity in the maze.
    Handles grid position, smooth movement interpolation, and game stats.
    """

    def __init__(self,
                 start_grid_x: int,
                 start_grid_y: int,
                 tile_size: int,
                 config: Config) -> None:
        self.grid_x: int = start_grid_x
        self.grid_y: int = start_grid_y

        self.current_direction: Tuple[int, int] = (0, 0)
        self.next_direction: Tuple[int, int] = (0, 0)

        self.speed: float = 2.0
        self.tile_size: int = tile_size

        self.progress: float = 0.0
        self.moving: bool = False

        self.lives: int = config.lives
        self.score: int = 0
        self.is_powered_up: bool = False
        self.is_alive: bool = True

    def update(self, maze: Maze) -> None:
        if self.moving:
            self.progress += self.speed / self.tile_size
            if self.progress >= 1.0:
                self.grid_x += self.current_direction[0]
                self.grid_y += self.current_direction[1]
                self.progress = 0.0
                self.moving = self._can_move(maze, self.current_direction)
                if not self.moving:
                    self.current_direction = (0, 0)
        else:
            if self._can_move(maze, self.next_direction):
                self.current_direction = self.next_direction
                self.moving = True

    def _can_move(self, maze: Maze, direction: Tuple[int, int]) -> bool:
        dir_to_wall = {(0, -1): 'N', (1, 0): 'E', (0, 1): 'S', (-1, 0): 'W'}
        wall = dir_to_wall.get(direction)
        if wall is None:
            return False
        return not maze.has_wall(self.grid_x, self.grid_y, wall)