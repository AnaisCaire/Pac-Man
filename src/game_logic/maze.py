import random
from collections.abc import Callable

from mazegenerator.mazegenerator import MazeGenerator

from .config import LevelMazeSize
from .entities.items import Pacgum, SuperPacgum

WALL_BITS = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
_OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
_DIRECTIONS = {
    'N': (0, -1),
    'E': (1, 0),
    'S': (0, 1),
    'W': (-1, 0),
}


class MazeGenerationError(RuntimeError):
    """Raised when a generated maze cannot safely start gameplay."""


def _generate_grid(maze_size: LevelMazeSize, seed: int) -> list[list[int]]:
    """Call the assigned A-Maze-ing package with the required options."""
    try:
        maze = MazeGenerator(size=(maze_size.width, maze_size.height),
                             seed=seed,
                             perfect=False)
    except Exception as error:
        raise MazeGenerationError(f"maze generator failed: {error}") from error
    return maze.maze  # type: ignore[no-any-return]


class Maze:
    """Validated adapter around the assigned A-Maze-ing maze grid."""

    def __init__(
        self,
        maze_size: LevelMazeSize,
        seed: int,
        grid_factory: Callable[[LevelMazeSize, int], list[list[int]]] = _generate_grid,
    ) -> None:
        self.grid = grid_factory(maze_size, seed)
        self._validate_grid(maze_size)
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        self.corners = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]

    def _validate_grid(self, maze_size: LevelMazeSize) -> None:
        """Reject malformed generator output before gameplay reads walls."""
        if len(self.grid) != maze_size.height:
            raise MazeGenerationError("maze height does not match configuration")
        if not self.grid or any(len(row) != maze_size.width for row in self.grid):
            raise MazeGenerationError("maze grid must be rectangular")
        for row in self.grid:
            for cell in row:
                if type(cell) is not int or not 0 <= cell <= 15:
                    raise MazeGenerationError("maze grid contains invalid cell values")

    def has_wall(self, x: int, y: int, direction: str) -> bool:
        """Return True if there is a wall in the given N/E/S/W direction."""
        if direction not in WALL_BITS:
            raise MazeGenerationError(f"unknown wall direction: {direction}")
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return (self.grid[y][x] & WALL_BITS[direction]) != 0

    def is_wall(self, x: int, y: int) -> bool:
        """Return True for impassable cells or out-of-bounds coordinates."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.grid[y][x] == 15

    def find_spawn(self) -> tuple[int, int]:
        """Return the nearest walkable cell to the maze center."""
        cx, cy = self.width // 2, self.height // 2
        for r in range(max(self.width, self.height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    x, y = cx + dx, cy + dy
                    if not self.is_wall(x, y):
                        return (x, y)
        raise MazeGenerationError("maze has no valid spawn cell")

    def _reachable_from(self, start: tuple[int, int]) -> set[tuple[int, int]]:
        """Return all walkable cells reachable from `start` using maze walls."""
        if self.is_wall(*start):
            return set()
        reachable = {start}
        frontier = [start]
        while frontier:
            x, y = frontier.pop()
            for direction, (dx, dy) in _DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if (nx, ny) in reachable or self.has_wall(x, y, direction):
                    continue
                if self.is_wall(nx, ny) or self.has_wall(nx, ny, _OPPOSITE[direction]):
                    continue
                reachable.add((nx, ny))
                frontier.append((nx, ny))
        return reachable

    def place_pacgums(
        self,
        spawn: tuple[int, int],
        count: int,
        points_per_pacgum: int,
        rng: random.Random,
        blocked: set[tuple[int, int]] | None = None,
    ) -> dict[tuple[int, int], Pacgum]:
        """Place reachable pacgums with an injected RNG source."""
        blocked = blocked or set()
        reachable = self._reachable_from(spawn)
        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) in reachable
            and (x, y) not in self.corners
            and (x, y) not in blocked
            and (x, y) != spawn
        ]
        count = min(count, len(candidates))
        return {
            (x, y): Pacgum(x, y, points_per_pacgum)
            for (x, y) in rng.sample(candidates, count)
        }

    def place_super_pacgums(
        self,
        points_per_super: int,
        spawn: tuple[int, int],
    ) -> dict[tuple[int, int], SuperPacgum]:
        """Place four super-pacgums in reachable corner regions."""
        reachable = self._reachable_from(spawn)
        chosen: list[tuple[int, int]] = []
        for corner_x, corner_y in self.corners:
            pos = self._find_near_corner(
                corner_x,
                corner_y,
                reachable,
                set(chosen) | {spawn},
            )
            chosen.append(pos)
        return {
            (cx, cy): SuperPacgum(cx, cy, points_per_super)
            for (cx, cy) in chosen
        }

    def _find_near_corner(
        self,
        cx: int,
        cy: int,
        reachable: set[tuple[int, int]],
        blocked: set[tuple[int, int]],
    ) -> tuple[int, int]:
        """Find the nearest reachable, unblocked cell to a corner."""
        for r in range(max(self.width, self.height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    x, y = cx + dx, cy + dy
                    if (x, y) in reachable and (x, y) not in blocked:
                        return (x, y)
        raise MazeGenerationError("cannot place mandatory corner item")

    def place_ghosts(
        self,
        spawn: tuple[int, int],
        blocked: set[tuple[int, int]] | None = None,
    ) -> list[tuple[int, int]]:
        """Place one ghost in each reachable corner region."""
        reachable = self._reachable_from(spawn)
        ghosts: list[tuple[int, int]] = []
        blocked = set(blocked or ())
        for corner_x, corner_y in self.corners:
            ghost = self._find_near_corner(
                corner_x,
                corner_y,
                reachable,
                blocked | {spawn},
            )
            ghosts.append(ghost)
            blocked.add(ghost)
        if len(ghosts) != 4:
            raise MazeGenerationError("expected four ghost positions")
        return ghosts
