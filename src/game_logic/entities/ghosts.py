from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Tuple
from .player import Player
from .entity import Entity
import random

if TYPE_CHECKING:
    from ..maze import Maze

GHOST_SPEED = 1.5

class GhostState(Enum):
    """
    The four operational states of a ghost.
    """
    SCATTER = 1     # Patrolling home corner
    CHASE = 2       # chase player
    FRIGHTENED = 3  # Vulnerable to being eaten (blue state)
    DEAD = 4        # Eaten


class Ghost(Entity):
    """
    Base ghost class. Handles movement, state machine, and behavior.
    Subclasses override _get_chase_target() to implement unique chase behaviour.
    """

    # image set identifier — subclasses override to pick their sprite
    sprite: str = 'red'

    def __init__(self,
                 start_grid_x: int,
                 start_grid_y: int,
                 tile_size: int,
                 player: Player,
                 start_time: int) -> None:
        super().__init__(start_grid_x, start_grid_y, tile_size)
        self.speed: float = GHOST_SPEED
        self.home_x: int = start_grid_x
        self.home_y: int = start_grid_y
        self.state: GhostState = GhostState.SCATTER
        self.state_timer: int = start_time
        self.player = player

    # --------------------------
    #       helper functions
    # --------------------------

    def _get_chase_target(self) -> tuple[int, int]:
        """
        Returns the target tile used in CHASE mode.
        Default: the player's current tile.
        Override in subclasses for unique ghost personalities.
        """
        return (self.player.grid_x, self.player.grid_y)

    def _can_move(self, maze: Maze, direction: Tuple[int, int]) -> bool:
        """
        Ghost cannot go backwards except when frightened.
        """
        # Prevent 180-degree turns unless frightened
        if self.current_direction != (0, 0) and self.state != GhostState.FRIGHTENED:
            opposite_direction = (-self.current_direction[0], -self.current_direction[1])
            if direction == opposite_direction:
                return False

        # guard: current position must be inside the grid
        if not (0 <= self.grid_x < maze.width and 0 <= self.grid_y < maze.height):
            return False

        # guard: target cell must also be in bounds and not a logo block (value 15)
        target_x = self.grid_x + direction[0]
        target_y = self.grid_y + direction[1]
        if not (0 <= target_x < maze.width and 0 <= target_y < maze.height):
            return False
        if maze.is_wall(target_x, target_y):
            return False

        return super()._can_move(maze, direction)

    def _choose_direction(self, maze: Maze) -> tuple[int, int]:
        """ Choose next direction based on current state and target tile. """
        possible_directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        valid_directions = []

        for d in possible_directions:
            if self._can_move(maze, d):
                valid_directions.append(d)

        # Fallback if totally stuck (shouldn't happen in a valid maze)
        if not valid_directions:
            return (0, 0)

        # Frightened: move randomly ?
        if self.state == GhostState.FRIGHTENED:
            return random.choice(valid_directions)

        # Determine target tile based on state
        target_x, target_y = self.grid_x, self.grid_y

        if self.state == GhostState.CHASE:
            target_x, target_y = self._get_chase_target()

        elif self.state in (GhostState.SCATTER, GhostState.DEAD):
            target_x, target_y = self.home_x, self.home_y

        # Greedy: pick the direction that minimises distance to target
        best_direction = valid_directions[0]
        min_distance = float('inf')

        for d in valid_directions:
            test_x = self.grid_x + d[0]
            test_y = self.grid_y + d[1]
            # squared distance avoids expensive sqrt call
            distance = (test_x - target_x) ** 2 + (test_y - target_y) ** 2
            if distance < min_distance:
                min_distance = distance
                best_direction = d

        return best_direction

    def _reverse_direction(self) -> None:
        """ Forces the ghost to instantly turn around. """
        if self.current_direction != (0, 0):
            self.current_direction = (-self.current_direction[0], -self.current_direction[1])
            self.progress = 1.0 - self.progress

    def _manage_state_timers(self, current_time: int) -> None:
        """ Handles the automatic switching between SCATTER, CHASE, and FRIGHTENED. """

        if self.state == GhostState.FRIGHTENED:
            if current_time - self.state_timer > self.player.power_up_duration:
                self.state = GhostState.CHASE
                self.state_timer = current_time
            return

        # wait until home tile is reached
        if self.state == GhostState.DEAD:
            if self.grid_x == self.home_x and self.grid_y == self.home_y:
                self.respawn(current_time)
            return

        time_in_state = current_time - self.state_timer

        if self.state == GhostState.SCATTER:
            if time_in_state > 7000: # should we hardcode it ?
                self.state = GhostState.CHASE
                self.state_timer = current_time
                self._reverse_direction()

        elif self.state == GhostState.CHASE:
            if time_in_state > 20000:
                self.state = GhostState.SCATTER
                self.state_timer = current_time
                self._reverse_direction()

    # --------------------------
    #    public functions
    # --------------------------

    def update(self, current_time: int, maze: Maze) -> None:
        """
        Update state timers and move the ghost one step.
        """
        self._manage_state_timers(current_time)

        # Pick initial direction if just spawned or respawned
        if self.current_direction == (0, 0):
            self.current_direction = self._choose_direction(maze)

        # Advance sub-tile progress
        self.progress += self.speed / self.tile_size
        if self.progress >= 1.0:
            self.grid_x += self.current_direction[0]
            self.grid_y += self.current_direction[1]
            # clamp to grid — prevents out-of-bounds if a wall bit is missing at an edge
            self.grid_x = max(0, min(maze.width - 1, self.grid_x))
            self.grid_y = max(0, min(maze.height - 1, self.grid_y))
            self.progress -= 1.0
            # Choose next direction at tile boundary
            self.current_direction = self._choose_direction(maze)

    @property
    def is_frightened(self) -> bool:
        """True when the ghost is vulnerable and can be eaten."""
        return self.state == GhostState.FRIGHTENED

    @property
    def is_dead(self) -> bool:
        """True when the ghost is returning home after being eaten."""
        return self.state == GhostState.DEAD

    def die(self) -> None:
        """
        Triggered when Pac-Man eats the ghost while FRIGHTENED.
        """
        self.state = GhostState.DEAD
        self.current_direction = (0, 0)

    def frighten(self, current_time: int) -> None:
        """
        Triggered when the player eats a Super Pacgum.
        Changes state to FRIGHTENED and reverses current direction.
        """
        self.state = GhostState.FRIGHTENED
        self.state_timer = current_time
        self._reverse_direction()

    def respawn(self, current_time: int) -> None:
        """
        Triggered when the ghost reaches the ghost house after being eaten.
        Resets position to home and state to standard SCATTER/CHASE.
        """
        self.grid_x = self.home_x
        self.grid_y = self.home_y
        self.current_direction = (0, 0)
        self.progress = 0.0
        self.state = GhostState.SCATTER
        self.state_timer = current_time
