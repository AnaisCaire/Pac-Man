from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..maze import Maze


class Entity:
    """Base class for all movable entities (player and ghosts)."""

    def __init__(self,
                 start_grid_x: int,
                 start_grid_y: int,
                 tile_size: int) -> None:
        self.grid_x: int = start_grid_x
        self.grid_y: int = start_grid_y
        self.tile_size: int = tile_size
        self.current_direction: Tuple[int, int] = (0, 0)
        self.progress: float = 0.0
        self.speed: float = 0.0

    def _can_move(self, maze: Maze, direction: Tuple[int, int]) -> bool:
        dir_to_wall = {(0, -1): 'N', (1, 0): 'E', (0, 1): 'S', (-1, 0): 'W'}
        wall = dir_to_wall.get(direction)
        if wall is None:
            return False
        return not maze.has_wall(self.grid_x, self.grid_y, wall)