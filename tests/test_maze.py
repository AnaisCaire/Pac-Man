"""Maze adapter and level-seed contract tests."""

from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from src.game_logic.config import LevelMazeSize
from src.game_logic.config import Config
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.player import Player
from src.game_logic.game_engine import select_level_seed
from src.game_logic.maze import Maze, MazeGenerationError, _generate_grid


SIZE = LevelMazeSize(15, 15)


def open_grid(width: int = 15, height: int = 15) -> list[list[int]]:
    """Return a fully open, rectangular maze grid."""
    return [[0 for _ in range(width)] for _ in range(height)]


class MazeAdapterTests(unittest.TestCase):
    """Protect the A-Maze-ing adapter and safe placement contracts."""

    def test_generator_adapter_uses_seed_size_and_perfect_false(self) -> None:
        """The assigned wheel is called through one explicit adapter seam."""
        calls: list[tuple[tuple[int, int], int, bool]] = []

        class FakeGenerator:
            def __init__(self, size: tuple[int, int], seed: int, perfect: bool) -> None:
                calls.append((size, seed, perfect))
                self.maze = open_grid(*size)

        with patch("src.game_logic.maze.MazeGenerator", FakeGenerator):
            grid = _generate_grid(LevelMazeSize(16, 17), 123)

        self.assertEqual(calls, [((16, 17), 123, False)])
        self.assertEqual(len(grid), 17)
        self.assertEqual(len(grid[0]), 16)

    def test_same_seed_same_grid_and_tested_different_seeds_differ(self) -> None:
        """The external generator remains structurally deterministic per seed."""
        first = Maze(SIZE, 42).grid
        second = Maze(SIZE, 42).grid
        seed_one = Maze(SIZE, 1).grid
        seed_two = Maze(SIZE, 2).grid

        self.assertEqual(first, second)
        self.assertNotEqual(seed_one, seed_two)

    def test_level_seed_policy_is_fixed_first_random_later(self) -> None:
        """Only level zero uses the configured seed; later levels use injected RNG."""
        rng = random.Random(7)
        expected_rng = random.Random(7)

        self.assertEqual(select_level_seed(42, 0, rng), 42)
        self.assertEqual(
            select_level_seed(42, 1, rng),
            expected_rng.randrange(0, 2 ** 31),
        )
        self.assertEqual(
            select_level_seed(42, 2, rng),
            expected_rng.randrange(0, 2 ** 31),
        )

    def test_malformed_generator_output_fails_before_gameplay(self) -> None:
        """Bad dimensions and cell values become clean maze errors."""
        with self.assertRaisesRegex(MazeGenerationError, "rectangular"):
            Maze(
                SIZE,
                1,
                grid_factory=lambda _size, _seed: [[0] * 15] * 14 + [[0]],
            )
        with self.assertRaisesRegex(MazeGenerationError, "invalid cell"):
            Maze(
                SIZE,
                1,
                grid_factory=lambda _size, _seed: [[16] * 15 for _ in range(15)],
            )

    def test_generator_exception_becomes_maze_error(self) -> None:
        """Import/constructor failures are wrapped at the adapter boundary."""
        class BrokenGenerator:
            def __init__(self, size: tuple[int, int], seed: int, perfect: bool) -> None:
                raise RuntimeError("boom")

        with patch("src.game_logic.maze.MazeGenerator", BrokenGenerator):
            with self.assertRaisesRegex(MazeGenerationError, "maze generator failed"):
                _generate_grid(SIZE, 42)

    def test_mandatory_placements_are_reachable_and_distinct(self) -> None:
        """Spawn, pellets, super-pellets, and ghosts use valid reachable cells."""
        maze = Maze(SIZE, 1, grid_factory=lambda _size, _seed: open_grid())
        spawn = maze.find_spawn()
        super_pacgums = maze.place_super_pacgums(50, spawn)
        pacgums = maze.place_pacgums(
            spawn,
            42,
            10,
            random.Random(42),
            blocked=set(super_pacgums),
        )
        ghosts = maze.place_ghosts(spawn)

        self.assertEqual(spawn, (7, 7))
        self.assertEqual(len(super_pacgums), 4)
        self.assertEqual(len(set(ghosts)), 4)
        self.assertTrue(all(not maze.is_wall(x, y) for x, y in super_pacgums))
        self.assertTrue(all(not maze.is_wall(x, y) for x, y in ghosts))
        self.assertNotIn(spawn, super_pacgums)
        self.assertNotIn(spawn, pacgums)
        self.assertTrue(set(pacgums).isdisjoint(super_pacgums))

    def test_pacgum_rng_is_injected_and_independent(self) -> None:
        """Pacgum placement depends on the provided RNG, not module-global random."""
        maze = Maze(SIZE, 1, grid_factory=lambda _size, _seed: open_grid())
        spawn = maze.find_spawn()
        first = maze.place_pacgums(spawn, 5, 10, random.Random(3))
        second = maze.place_pacgums(spawn, 5, 10, random.Random(3))
        different = maze.place_pacgums(spawn, 5, 10, random.Random(4))

        self.assertEqual(set(first), set(second))
        self.assertNotEqual(set(first), set(different))

    def test_impossible_mandatory_placement_fails_cleanly(self) -> None:
        """A level without four reachable corner regions must not start."""
        grid = [[15 for _ in range(15)] for _ in range(15)]
        grid[7][7] = 0
        maze = Maze(SIZE, 1, grid_factory=lambda _size, _seed: grid)

        with self.assertRaisesRegex(MazeGenerationError, "mandatory corner"):
            maze.place_super_pacgums(50, maze.find_spawn())

    def test_frightened_ghost_rng_is_injected(self) -> None:
        """Frightened tie-breaking uses the ghost RNG, not module-global random."""
        maze = Maze(SIZE, 1, grid_factory=lambda _size, _seed: open_grid())
        player = Player(7, 7, 1, Config())
        first = Ghost(7, 7, 1, player, 0, random.Random(5))
        second = Ghost(7, 7, 1, player, 0, random.Random(5))
        first.state = GhostState.FRIGHTENED
        second.state = GhostState.FRIGHTENED

        self.assertEqual(first._choose_direction(maze), second._choose_direction(maze))


if __name__ == "__main__":
    unittest.main()
