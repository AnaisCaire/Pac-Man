from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from ..config import Config
from .entity import Entity
from .items import Pacgum, SuperPacgum
import pygame  # only for pygame.event.Event / key constants in handle_input()

if TYPE_CHECKING:
    from ..maze import Maze
    from .ghosts import Ghost

PLAYER_SPEED = 2.5


class Player(Entity):
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
        super().__init__(start_grid_x, start_grid_y, tile_size)
        self.speed: float = PLAYER_SPEED
        self.next_direction: Tuple[int, int] = (0, 0)
        self.moving: bool = False

        # remember spawn so we can reset position on respawn
        self.spawn_x: int = start_grid_x
        self.spawn_y: int = start_grid_y

        self.lives: int = config.lives
        self.score: int = 0
        self.points_per_ghost: int = config.points_per_ghost
        # --- handle state ----
        self.is_powered_up: bool = False
        self.power_up_start_time: int = 0
        self.power_up_duration: int = 5000
        self.is_alive: bool = True

        # death animation state
        self.is_dying: bool = False
        self.death_progress: float = 0.0  # 0.0 = full size, 1.0 = fully shrunk
        self.death_time: int = 0          # timestamp when animation finished
        self.respawn_delay: int = 3000    # ms to wait before respawning

        # invincibility after respawn — prevents instant re-death
        self.is_invincible: bool = False
        self.invincibility_start: int = 0
        self.invincibility_duration: int = 2000  # 2 seconds

    def update(self, maze: Maze) -> None:
        """Advance the player one frame: handle movement and wall collisions."""
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
                    self.current_direction = (0, 0)
        else:
            if self._can_move(maze, self.next_direction):
                self.current_direction = self.next_direction
                self.moving = True

    def update_timers(self, current_time: int) -> None:
        """Check if any active timers have expired.

        `current_time` is milliseconds from the caller's project clock —
        this domain method never reads a wall clock itself.
        """
        if self.is_powered_up:
            if current_time - self.power_up_start_time >= self.power_up_duration:
                self.is_powered_up = False

        # advance death animation
        if self.is_dying:
            self.death_progress += 0.02
            if self.death_progress >= 1.0:
                # animation finished — lose a life and start respawn countdown
                self.death_progress = 1.0
                self.is_dying = False
                self.is_alive = False
                self.lives -= 1
                self.death_time = current_time

        # respawn after delay if still has lives
        if not self.is_alive and self.lives > 0:
            if current_time - self.death_time >= self.respawn_delay:
                self.respawn(current_time)

        # expire invincibility window
        if self.is_invincible:
            if current_time - self.invincibility_start >= self.invincibility_duration:
                self.is_invincible = False

    def start_death_animation(self) -> None:
        """Freeze movement and begin the shrink animation."""
        if not self.is_dying:
            self.is_dying = True
            self.death_progress = 0.0
            self.moving = False
            self.current_direction = (0, 0)

    def respawn(self, current_time: int) -> None:
        """Reset position and state back to the spawn tile."""
        self.grid_x = self.spawn_x
        self.grid_y = self.spawn_y
        self.progress = 0.0
        self.moving = False
        self.current_direction = (0, 0)
        self.next_direction = (0, 0)
        self.is_dying = False
        self.death_progress = 0.0
        self.is_alive = True
        # grant brief invincibility so a ghost on the spawn tile can't kill instantly
        self.is_invincible = True
        self.invincibility_start = current_time

    def activate_power_up(self, current_time: int) -> None:
        """Trigger the power-up state and record the exact time."""
        self.is_powered_up = True
        self.power_up_start_time = current_time

    def check_ghost_collision(self, ghosts: list[Ghost]) -> None:
        """Check if the player overlaps any ghost and react accordingly."""
        if self.is_dying or not self.is_alive or self.is_invincible:
            return

        for ghost in ghosts:
            if ghost.grid_x == self.grid_x and ghost.grid_y == self.grid_y:
                if ghost.is_frightened:
                    self.score += self.points_per_ghost
                    ghost.die()
                elif not ghost.is_dead:
                    self.start_death_animation()
                    return  # one collision is enough per frame

    def check_item_collision(self,
                             pacgums: dict[tuple[int, int], Pacgum],
                             super_pacgums: dict[tuple[int, int], SuperPacgum],
                             current_time: int) -> None:
        """Remove pacgum or super pacgum if eaten and update score."""
        pos = (self.grid_x, self.grid_y)
        if pos in pacgums:
            self.score += pacgums.pop(pos).points
        elif pos in super_pacgums:
            self.score += super_pacgums.pop(pos).points
            self.activate_power_up(current_time)


def resolve_collisions(
    player: Player,
    pacgums: dict[tuple[int, int], Pacgum],
    super_pacgums: dict[tuple[int, int], SuperPacgum],
    ghosts: list[Ghost],
    current_time: int,
) -> None:
    """Resolve items before ghosts, so a same-tile super-pacgum wins."""
    was_powered_up = player.is_powered_up
    player.check_item_collision(pacgums, super_pacgums, current_time)
    if player.is_powered_up and not was_powered_up:
        for ghost in ghosts:
            ghost.frighten(current_time, reverse=False)
    player.check_ghost_collision(ghosts)
    if player.is_powered_up and not was_powered_up:
        for ghost in ghosts:
            ghost.frighten(current_time)


def handle_input(player: Player, events: list[pygame.event.Event]) -> None:
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
