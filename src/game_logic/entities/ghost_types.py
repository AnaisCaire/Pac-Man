from .ghosts import Ghost
from .player import Player


class Blinky(Ghost):
    """Red ghost — directly chases Pac-Man."""
    sprite = 'red'


class Pinky(Ghost):
    """
    Pink ghost — targets 4 tiles in front of Pac-Man's current direction.
    If Pac-Man is moving right, Pinky aims at (player_x + 4, player_y).
    """
    sprite = 'pink'

    def _get_chase_target(self) -> tuple[int, int]:
        dx, dy = self.player.current_direction
        # aim 4 tiles ahead of where Pac-Man is facing
        target_x = self.player.grid_x + dx * 4
        target_y = self.player.grid_y + dy * 4
        return (target_x, target_y)


class Inky(Ghost):
    """
    Cyan ghost — uses both Blinky's position and Pac-Man's position to pick a target.
    Algorithm:
      1. Find the tile 2 ahead of Pac-Man → call it P
      2. Draw a vector from Blinky to P, then double it → that's Inky's target
    Inky needs a reference to Blinky so the game engine must pass it after creation.
    """
    sprite = 'cyan'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # set after construction: inky.blinky = blinky_instance
        self.blinky: Ghost | None = None

    def _get_chase_target(self) -> tuple[int, int]:
        # fall back to direct chase if Blinky reference is not set
        if self.blinky is None:
            return (self.player.grid_x, self.player.grid_y)

        dx, dy = self.player.current_direction
        # pivot point: 2 tiles ahead of Pac-Man
        pivot_x = self.player.grid_x + dx * 2
        pivot_y = self.player.grid_y + dy * 2
        # double the vector from Blinky to the pivot
        target_x = pivot_x + (pivot_x - self.blinky.grid_x)
        target_y = pivot_y + (pivot_y - self.blinky.grid_y)
        return (target_x, target_y)


class Clyde(Ghost):
    """
    Yellow ghost — chases Pac-Man when far away, scatters to home when close.
    Threshold: if squared distance to player > 8^2 (64), chase; otherwise scatter.
    """
    sprite = 'yellow'

    def _get_chase_target(self) -> tuple[int, int]:
        dx = self.player.grid_x - self.grid_x
        dy = self.player.grid_y - self.grid_y
        squared_distance = dx * dx + dy * dy
        # switch to home corner when within 8 tiles
        if squared_distance <= 64:
            return (self.home_x, self.home_y)
        return (self.player.grid_x, self.player.grid_y)
