"""Deterministic contracts for ghost personalities and lifecycle."""

from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from src.game_logic.config import Config, LevelMazeSize
from src.game_logic.entities.ghost_types import Blinky, Clyde, Inky, Pinky
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.player import Player
from src.game_logic.maze import Maze


TRAP_GRID = [
    [9, 7, 15],
    [10, 15, 11],
    [12, 5, 6],
]


def fixture_maze(grid: list[list[int]]) -> Maze:
    """Build a Maze from a hand-written wall-bit grid."""
    size = LevelMazeSize(len(grid[0]), len(grid))
    return Maze(size, 0, grid_factory=lambda _size, _seed: grid)


class GhostPersonalityTests(unittest.TestCase):
    """Each named ghost keeps its documented chase target."""

    def test_chase_targets_remain_distinct(self) -> None:
        player = Player(5, 5, 16, Config())
        player.current_direction = (1, 0)
        blinky = Blinky(1, 1, 16, player, 0)
        pinky = Pinky(2, 1, 16, player, 0)
        inky = Inky(3, 1, 16, player, 0)
        clyde = Clyde(15, 15, 16, player, 0)
        inky.blinky = blinky

        self.assertEqual(blinky._get_chase_target(), (5, 5))
        self.assertEqual(pinky._get_chase_target(), (9, 5))
        self.assertEqual(inky._get_chase_target(), (13, 9))
        self.assertEqual(clyde._get_chase_target(), (5, 5))

        clyde.grid_x, clyde.grid_y = (6, 5)
        self.assertEqual(clyde._get_chase_target(), (15, 15))


class GhostDirectionTests(unittest.TestCase):
    """State-specific choices stay legal, purposeful, and non-stalling."""

    def test_frightened_ghost_maximizes_distance_from_player(self) -> None:
        maze = fixture_maze([[0, 0, 0] for _ in range(3)])
        player = Player(1, 0, 16, Config())
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.state = GhostState.FRIGHTENED

        with patch.object(ghost.rng, "choice") as choice:
            self.assertEqual(ghost._choose_direction(maze), (0, 1))

        choice.assert_not_called()

    def test_frightened_rng_only_breaks_max_distance_ties(self) -> None:
        maze = fixture_maze([[0, 0, 0] for _ in range(3)])
        player = Player(0, 0, 16, Config())
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.state = GhostState.FRIGHTENED

        with patch.object(ghost.rng, "choice", return_value=(1, 0)) as choice:
            self.assertEqual(ghost._choose_direction(maze), (1, 0))

        choice.assert_called_once_with([(0, 1), (1, 0)])

    def test_normal_ghost_reverses_only_when_a_dead_end_requires_it(self) -> None:
        maze = fixture_maze(TRAP_GRID)
        player = Player(2, 1, 16, Config())
        ghost = Ghost(1, 0, 16, player, 0)
        ghost.state = GhostState.CHASE
        ghost.current_direction = (1, 0)

        self.assertEqual(ghost._choose_direction(maze), (-1, 0))

        open_maze = fixture_maze([[0, 0, 0] for _ in range(3)])
        ghost.grid_x, ghost.grid_y = (1, 1)
        self.assertNotEqual(ghost._choose_direction(open_maze), (-1, 0))


class GhostLifecycleTests(unittest.TestCase):
    """Eaten ghosts visibly return through the maze and respawn."""

    def test_dead_eyes_move_twice_as_fast_as_a_live_ghost(self) -> None:
        maze = fixture_maze([[0, 0, 0] for _ in range(3)])
        player = Player(2, 1, 16, Config())
        live = Ghost(1, 1, 16, player, 0)
        dead = Ghost(1, 1, 16, player, 0)
        live.state = GhostState.CHASE
        dead.state = GhostState.DEAD
        live.current_direction = (1, 0)
        dead.current_direction = (1, 0)
        dead.home_x, dead.home_y = (2, 1)

        live.update(0, maze)
        dead.update(0, maze)

        self.assertEqual(dead.progress, live.progress * 2)

    def test_dead_eyes_retarget_before_respawning_at_a_safe_corner(self) -> None:
        player = Player(0, 0, 16, Config())
        ghost = Ghost(0, 0, 16, player, 0)
        ghost.home_positions = [(0, 0), (14, 0)]
        ghost.state = GhostState.DEAD

        ghost._manage_state_timers(100)

        self.assertIs(ghost.state, GhostState.DEAD)
        self.assertEqual((ghost.grid_x, ghost.grid_y), (0, 0))
        self.assertEqual((ghost.home_x, ghost.home_y), (14, 0))

        ghost.grid_x, ghost.grid_y = (14, 0)
        ghost._manage_state_timers(200)

        self.assertIs(ghost.state, GhostState.SCATTER)
        self.assertEqual((ghost.grid_x, ghost.grid_y), (14, 0))

    def test_dead_ghost_follows_shortest_route_home_and_respawns(self) -> None:
        maze = fixture_maze(TRAP_GRID)
        player = Player(0, 0, 16, Config())
        ghost = Ghost(0, 1, 16, player, 0)
        ghost.home_x, ghost.home_y = (2, 1)
        ghost.home_positions = [(2, 1)]
        ghost.state = GhostState.DEAD

        self.assertEqual(ghost._choose_direction(maze), (0, 1))

        visited = []
        for current_time in range(100):
            visited.append((ghost.grid_x, ghost.grid_y))
            ghost.update(current_time, maze)
            if ghost.state is not GhostState.DEAD:
                break

        self.assertIn((0, 2), visited)
        self.assertIn((2, 2), visited)
        self.assertEqual((ghost.grid_x, ghost.grid_y), (2, 1))
        self.assertIs(ghost.state, GhostState.SCATTER)

    def test_moving_ghost_does_not_teleport_when_eaten(self) -> None:
        player = Player(1, 1, 16, Config())
        ghost = Ghost(1, 1, 16, player, 0)
        ghost.current_direction = (1, 0)
        ghost.progress = 0.75
        visual_position = (
            ghost.grid_x + ghost.progress * ghost.current_direction[0],
            ghost.grid_y + ghost.progress * ghost.current_direction[1],
        )

        ghost.die()

        self.assertEqual(
            (
                ghost.grid_x + ghost.progress * ghost.current_direction[0],
                ghost.grid_y + ghost.progress * ghost.current_direction[1],
            ),
            visual_position,
        )
        self.assertIs(ghost.state, GhostState.DEAD)

    def test_state_timers_transition_at_the_exact_boundary(self) -> None:
        player = Player(1, 1, 16, Config())
        ghost = Ghost(2, 1, 16, player, 0)

        ghost._manage_state_timers(7000)
        self.assertIs(ghost.state, GhostState.CHASE)

        ghost._manage_state_timers(27_000)
        self.assertIs(ghost.state, GhostState.SCATTER)

        ghost.frighten(30_000, reverse=False)
        ghost._manage_state_timers(30_000 + player.power_up_duration)
        self.assertIs(ghost.state, GhostState.CHASE)


if __name__ == "__main__":
    unittest.main()
