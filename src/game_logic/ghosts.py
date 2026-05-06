from enum import Enum
from typing import Tuple
from .maze import Maze
from .player import Player
import random

class GhostState(Enum):
    """
    The four  operational states of ghost.
    """
    SCATTER = 1     # Patrolling their home corner
    CHASE = 2       #  pursuing player
    FRIGHTENED = 3  # Vulnerable to being eaten (blue state)
    DEAD = 4        # Eaten, floating eyes returning to the ghost house


class Ghost:
    """
    Represents a ghost enemy in the maze.
    Handles AI state, movement, and interactions with the player.
    """

    def __init__(self,
                 start_grid_x: int,
                 start_grid_y: int,
                 color: Tuple[int, int, int],
                 tile_size: int,
                 player: Player,
                 start_time: int) -> None:
        """
        Initialize the ghost with its home coordinates, color, and movement stats.
        """
        # --- Home and color ---
        self.home_x: int = start_grid_x
        self.home_y: int = start_grid_y
        self.color: Tuple[int, int, int] = color

        # --- State Management ---
        self.state: GhostState = GhostState.SCATTER
        self.state_timer: int = start_time

        # --- Grid Position ---
        self.grid_x: int = start_grid_x
        self.grid_y: int = start_grid_y
        self.tile_size = tile_size

        # --- Movement ---
        self.current_direction: Tuple[int, int] = (0, 0)
        self.next_direction: Tuple[int, int] = (0, 0)
        self.progress: float = 0.0
        self.speed: float = 2.0  # Pixels per frame

        # --- get the player posi
        self.player = player


    # --------------------------
    #       helper functions
    # --------------------------

    def _can_move(self, maze: Maze, direction: Tuple[int, int]) -> bool:
        """ ghost cannt go backwards except when frightenend"""
        # If the ghost is moving, and NOT frightened, prevent 180-degree turns
        if self.current_direction != (0, 0) and self.state != GhostState.FRIGHTENED:
            opposite_direction = (-self.current_direction[0], -self.current_direction[1])
            if direction == opposite_direction:
                return False  # Reversal forbidden!

        dir_to_wall = {(0, -1): 'N', (1, 0): 'E', (0, 1): 'S', (-1, 0): 'W'}
        wall = dir_to_wall.get(direction)
        if wall is None:
            return False
        return not maze.has_wall(self.grid_x, self.grid_y, wall)
    
    def _choose_direction(self, maze: Maze) -> tuple[int, int]:
        """ based on state """
        possible_directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        valid_directions = []

        # 1. Gather all  moves
        for d in possible_directions:
            if self._can_move(maze, d):
                valid_directions.append(d)

        # Fallback if totally stuck (shouldn't happen in a valid maze)
        if not valid_directions:
            return (0, 0)

        if self.state == GhostState.FRIGHTENED:
            return random.choice(valid_directions)

        # 3. Determine the Target Tile based on the current state
        target_x, target_y = self.grid_x, self.grid_y

        if self.state == GhostState.CHASE:
            target_x, target_y = self.player.grid_x, self.player.grid_y
            
        elif self.state == GhostState.SCATTER:
            target_x, target_y = self.home_x, self.home_y
            
        elif self.state == GhostState.DEAD:
            target_x, target_y = self.home_x, self.home_y 

        # 4. Find the direction that brings us closest to the target tile
        best_direction = valid_directions[0]
        min_distance = float('inf')

        # greedy algo
        for d in valid_directions:
            test_x = self.grid_x + d[0]
            test_y = self.grid_y + d[1]
            # using squared distance to save CPU/math.sqrt calls
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
        
        # 1. Handle FRIGHTENED expiration
        if self.state == GhostState.FRIGHTENED:
            # Assuming a 5-second (5000ms) frightened duration
            if current_time - self.state_timer > self.player.power_up_duration: 
                self.state = GhostState.CHASE  # Default back to chase
                self.state_timer = current_time # Reset timer anchor
            return # Skip the wave logic if we are running for our lives!

        # 2. Handle DEAD state (Wait until we reach home to respawn)
        if self.state == GhostState.DEAD:
            if self.grid_x == self.home_x and self.grid_y == self.home_y:
                self.respawn()
            return

        # 3. The SCATTER / CHASE Wave System
        time_in_state = current_time - self.state_timer

        if self.state == GhostState.SCATTER:
            # Scatter for 7 seconds, then Chase
            if time_in_state > 7000:
                self.state = GhostState.CHASE
                self.state_timer = current_time
                self._reverse_direction()

        elif self.state == GhostState.CHASE:
            # Chase for 20 seconds, then Scatter
            if time_in_state > 20000:
                self.state = GhostState.SCATTER
                self.state_timer = current_time
                self._reverse_direction()

    # --------------------------
    #    public functions
    # --------------------------

    def update(self, current_time: int, maze: 'Maze') -> None:
        """
        Update the ghost's behavior, state timers, and position based on its current AI state.
        (Needs maze to check walls, and player to calculate targeting).
        """
        self._manage_state_timers(current_time)
        # start mouvement
        if self.current_direction == (0,0):
            self.current_direction = self._choose_direction(maze)
        
        # move accros pixels:
        self.progress += self.speed / self.tile_size
        # 4. Check if the ghost has reached the center of the next tile
        if self.progress >= 1.0:
            # Update mathematical grid position
            self.grid_x += self.current_direction[0]
            self.grid_y += self.current_direction[1]
            
            # Carry over the excess progress to prevent stuttering
            self.progress -= 1.0 

            # The exact moment a ghost enters a new tile, it looks at the adjacent 
            # paths and chooses the best direction for its next move!
            self.current_direction = self._choose_direction(maze)
        

    def frighten(self) -> None:
        """
        Triggered when the player eats a Super Pacgum. 
        Changes state to FRIGHTENED and reverses current direction.
        """
        pass

    def respawn(self) -> None:
        """
        Triggered when the ghost reaches the ghost house after being eaten.
        Resets position to home and state to standard SCATTER/CHASE.
        """
        pass