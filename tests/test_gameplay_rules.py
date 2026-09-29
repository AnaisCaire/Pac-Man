"""Focused regressions for observed gameplay rules."""

from __future__ import annotations

import random
import unittest

import pygame

from src.game_logic.config import Config, LevelMazeSize
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.items import Pacgum, SuperPacgum
from src.game_logic.entities.player import Player, handle_input, resolve_collisions
from src.game_logic.game_engine import GameState, terminal_state
from src.game_logic.maze import Maze


class GameplayRuleTests(unittest.TestCase):
    """Protect immediate item consumption and continuous ghost movement."""

    def test_collectibles_score_once_with_configured_values(self) -> None:
        """Pacgums and super-pacgums add their points only on first contact."""
        player = Player(1, 1, 16, Config(
            points_per_pacgum=11,
            points_per_super_pacgum=22,
        ))
        pacgums = {(1, 1): Pacgum(1, 1, 11)}
        super_pacgums = {(2, 1): SuperPacgum(2, 1, 22)}

        player.check_item_collision(pacgums, super_pacgums, 100)
        player.check_item_collision(pacgums, super_pacgums, 100)
        player.grid_x = 2
        player.check_item_collision(pacgums, super_pacgums, 200)
        player.check_item_collision(pacgums, super_pacgums, 200)

        self.assertEqual(player.score, 33)
        self.assertEqual(pacgums, {})
        self.assertEqual(super_pacgums, {})

    def test_super_pacgum_resolves_before_same_tile_ghost_collision(self) -> None:
        """Items activate power-up before same-frame ghost collisions resolve."""
        config = Config(points_per_super_pacgum=22, points_per_ghost=33)
        player = Player(1, 1, 16, config)
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        super_pacgums = {(1, 1): SuperPacgum(1, 1, 22)}

        resolve_collisions(player, {}, super_pacgums, [ghost], 100)

        self.assertEqual(player.score, 55)
        self.assertTrue(player.is_alive)
        self.assertFalse(player.is_dying)
        self.assertEqual(ghost.state, GhostState.DEAD)

    def test_each_frightened_ghost_scores_once(self) -> None:
        """A DEAD ghost cannot score again during repeated collision frames."""
        player = Player(1, 1, 16, Config(points_per_ghost=33))
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.state = GhostState.FRIGHTENED

        player.check_ghost_collision([ghost])
        player.check_ghost_collision([ghost])

        self.assertEqual(player.score, 33)
        self.assertEqual(ghost.state, GhostState.DEAD)

    def test_lethal_collision_loses_one_life_then_respawns_once(self) -> None:
        """Repeated collision frames do not duplicate the death transition."""
        player = Player(1, 1, 16, Config(lives=2))
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))

        player.check_ghost_collision([ghost])
        player.check_ghost_collision([ghost])
        player.death_progress = 0.98
        player.update_timers(100)
        player.update_timers(3099)
        self.assertFalse(player.is_alive)
        player.update_timers(3100)

        self.assertEqual(player.lives, 1)
        self.assertTrue(player.is_alive)
        self.assertTrue(player.is_invincible)

    def test_last_life_stays_dead_after_death_animation(self) -> None:
        """A zero-life player does not respawn after a lethal collision."""
        player = Player(1, 1, 16, Config(lives=1))
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))

        player.check_ghost_collision([ghost])
        player.death_progress = 0.98
        player.update_timers(100)
        player.update_timers(10_000)

        self.assertEqual(player.lives, 0)
        self.assertFalse(player.is_alive)
        self.assertFalse(player.is_dying)

    def test_last_collectible_lethal_collision_waits_for_death_outcome(self) -> None:
        """A lethal same-frame collision cannot produce premature victory."""
        player = Player(1, 1, 16, Config(lives=1))
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        pacgums = {(1, 1): Pacgum(1, 1, 10)}

        resolve_collisions(player, pacgums, {}, [ghost], 100)

        self.assertTrue(player.is_dying)
        self.assertIsNone(terminal_state(player, pacgums, {}))
        player.death_progress = 0.98
        player.update_timers(200)
        self.assertEqual(terminal_state(player, pacgums, {}), GameState.GAME_OVER)

    def test_timeout_has_priority_over_a_same_frame_collision(self) -> None:
        """Timeout ends the level before collisions are processed that frame."""
        player = Player(1, 1, 16, Config(lives=1))
        pacgums = {(1, 1): Pacgum(1, 1, 10)}

        self.assertEqual(
            terminal_state(player, pacgums, {}, timed_out=True),
            GameState.GAME_OVER,
        )

    def test_frightened_collision_at_expiry_still_scores_before_timers(self) -> None:
        """Collision resolution uses the state visible at that frame's start."""
        player = Player(1, 1, 16, Config(points_per_ghost=33))
        player.activate_power_up(0)
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.home_x = 2
        ghost.state = GhostState.FRIGHTENED
        ghost.state_timer = 0

        resolve_collisions(player, {}, {}, [ghost], player.power_up_duration)
        player.update_timers(player.power_up_duration)
        ghost._manage_state_timers(player.power_up_duration)

        self.assertEqual(player.score, 33)
        self.assertEqual(ghost.state, GhostState.DEAD)
        self.assertFalse(player.is_powered_up)

    def test_super_pacgum_scores_a_moving_ghost_on_the_same_tile(self) -> None:
        """Frightening cannot move an overlapping ghost before collision resolves."""
        config = Config(points_per_super_pacgum=22, points_per_ghost=33)
        player = Player(1, 1, 16, config)
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.current_direction = (1, 0)
        ghost.progress = 0.5
        super_pacgums = {(1, 1): SuperPacgum(1, 1, 22)}

        resolve_collisions(player, {}, super_pacgums, [ghost], 100)

        self.assertEqual(player.score, 55)
        self.assertEqual(ghost.state, GhostState.DEAD)

    def test_super_pacgum_does_not_resurrect_a_dead_ghost(self) -> None:
        """A returning ghost stays DEAD and cannot be scored again."""
        config = Config(points_per_super_pacgum=22, points_per_ghost=33)
        player = Player(1, 1, 16, config)
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        ghost.state = GhostState.DEAD
        super_pacgums = {(1, 1): SuperPacgum(1, 1, 22)}

        resolve_collisions(player, {}, super_pacgums, [ghost], 100)

        self.assertEqual(player.score, 22)
        self.assertEqual(ghost.state, GhostState.DEAD)

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

    def test_ghost_homes_can_overlap_super_pacgums(self) -> None:
        maze = Maze(LevelMazeSize(15, 15), 42)
        spawn = maze.find_spawn()
        super_pacgums = maze.place_super_pacgums(50, spawn)

        ghosts = maze.place_ghosts(spawn)

        self.assertEqual(len(ghosts), 4)
        self.assertEqual(len(set(ghosts)), 4)
        self.assertEqual(set(ghosts), set(super_pacgums))

    def test_respawn_uses_another_corner_when_home_is_too_close(self) -> None:
        player = Player(0, 0, 16, Config())
        ghost = Ghost(0, 0, 16, player, 0, random.Random(1))
        ghost.home_positions = [(0, 0), (14, 0), (0, 14), (14, 14)]

        ghost.respawn(100)

        self.assertEqual((ghost.grid_x, ghost.grid_y), (14, 0))
        self.assertGreaterEqual(
            abs(ghost.grid_x - player.grid_x) + abs(ghost.grid_y - player.grid_y),
            5,
        )

    def test_arrow_and_wasd_keys_map_to_the_four_directions(self) -> None:
        player = Player(1, 1, 16, Config())
        expected = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0),
        }

        for key, direction in expected.items():
            handle_input(player, [pygame.event.Event(pygame.KEYDOWN, key=key)])
            self.assertEqual(player.next_direction, direction)

        handle_input(player, [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
        ])
        self.assertEqual(player.next_direction, (0, -1))


if __name__ == "__main__":
    unittest.main()
