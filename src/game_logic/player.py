from typing import Tuple
from .config import Config
from .maze import Maze
import pygame

class Player:
    """
    Represents the player entity in the maze.
    Handles grid position
    smooth movement interpolation
    handle inputs
    game stats.
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
        # --- handle state ----
        self.is_powered_up: bool = False
        self.power_up_start_time: int = 0
        self.power_up_duration: int = 5000
        self.is_alive: bool = True

        # helper functions:

    def _can_move(self, maze: Maze, direction: Tuple[int, int]) -> bool:
        dir_to_wall = {(0, -1): 'N', (1, 0): 'E', (0, 1): 'S', (-1, 0): 'W'}
        wall = dir_to_wall.get(direction)
        if wall is None:
            return False
        return not maze.has_wall(self.grid_x, self.grid_y, wall)

    def update(self, maze: Maze) -> None:
        """
        player mouvement
        """
        if self.moving:
            self.progress += self.speed / self.tile_size
            if self.progress >= 1.0:
                self.grid_x += self.current_direction[0]
                self.grid_y += self.current_direction[1]
                self.progress = 0.0
                # try to turn
                if self._can_move(maze, self.next_direction):
                    self.current_direction = self.next_direction
                    self.moving = True
                elif self._can_move(maze, self.current_direction):
                    self.moving = True
                # hits a wall
                else:
                    self.moving = False
                    self.current_direction = (0,0)
        else:
            if self._can_move(maze, self.next_direction):
                self.current_direction = self.next_direction
                self.moving = True
    
    def update_timers(self) -> None:
        """Check if any active timers have expired."""
        if self.is_powered_up:
            current_time = pygame.time.get_ticks()
            # If current time minus start time is greater than the duration
            if current_time - self.power_up_start_time >= self.power_up_duration:
                # Time is up! Remove the power-up.
                self.is_powered_up = False

    def activate_power_up(self) -> None:
        """Trigger the power-up state and record the exact time."""
        self.is_powered_up = True
        self.power_up_start_time = pygame.time.get_ticks()

def check_collision(player: Player,
                    pacgums: set[tuple[int, int]],
                    super_pacgums: set[tuple[int, int]],
                    points_per_pacgum: int,
                    point_per_superpacgum: int) -> None:
    """ remove pacgum if eaten """
    if (player.grid_x, player.grid_y) in pacgums:
        if player.progress >= 0.01:
            pacgums.remove((player.grid_x, player.grid_y))
            player.score += points_per_pacgum
    if (player.grid_x, player.grid_y) in super_pacgums:
        if player.progress >= 0.01:
            super_pacgums.remove((player.grid_x, player.grid_y))
            player.activate_power_up()
            player.score += point_per_superpacgum

def handle_input(player: Player, events: list) -> None:
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                player.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                player.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                player.next_direction = (1, 0)
