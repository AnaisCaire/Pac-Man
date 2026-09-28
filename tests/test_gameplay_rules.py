"""Focused regressions for observed gameplay rules."""

from __future__ import annotations

import random
import unittest

from src.game_logic.config import Config, LevelMazeSize
from src.game_logic.entities.ghosts import Ghost
from src.game_logic.entities.items import SuperPacgum
from src.game_logic.entities.player import Player
from src.game_logic.maze import Maze


class GameplayRuleTests(unittest.TestCase):
    """Protect immediate item consumption and continuous ghost movement."""

    def test_entering_a_super_pacgum_tile_consumes_it_immediately(self) -> None:
        config = Config()
        player = Player(1, 1, 16, config)
        super_pacgums = {(1, 1): SuperPacgum(1, 1, 50)}

        player.check_item_collision({}, super_pacgums, 100)

        self.assertEqual(super_pacgums, {})
        self.assertEqual(player.score, 50)
        self.assertTrue(player.is_powered_up)

    def test_reversing_mid_tile_keeps_ghost_at_the_same_position(self) -> None:
        player = Player(7, 7, 16, Config())
        ghost = Ghost(3, 4, 16, player, 0, random.Random(1))
        ghost.current_direction = (1, 0)
        ghost.progress = 0.25

        ghost._reverse_direction()

        self.assertEqual((ghost.grid_x, ghost.grid_y), (4, 4))
        self.assertEqual(ghost.current_direction, (-1, 0))
        self.assertEqual(ghost.progress, 0.75)

    def test_ghost_homes_do_not_overlap_super_pacgums(self) -> None:
        maze = Maze(LevelMazeSize(15, 15), 42)
        spawn = maze.find_spawn()
        super_pacgums = maze.place_super_pacgums(50, spawn)

        ghosts = maze.place_ghosts(spawn, blocked=set(super_pacgums))

        self.assertEqual(len(ghosts), 4)
        self.assertEqual(len(set(ghosts)), 4)
        self.assertTrue(set(ghosts).isdisjoint(super_pacgums))


if __name__ == "__main__":
    unittest.main()
