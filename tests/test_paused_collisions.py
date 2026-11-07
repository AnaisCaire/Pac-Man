"""Collision rules on frames where Pause or Evaluator Freeze is involved.

Each test replays frames in `_run_gameplay` order: resolve collisions, then
player timers, then ghost timers (skipped while frozen), all at the time the
loop would pass in.
"""

from __future__ import annotations

import random
import unittest

from src.game_logic.clock import ProjectClock
from src.game_logic.config import Config
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.player import Player, resolve_collisions
from src.game_logic.evaluator import EvaluatorMode


class FakeMonotonic:
    """Controllable monotonic source expressed in seconds."""

    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


def _powered_player_and_ghosts(
    start_time: int,
) -> tuple[Player, Ghost, Ghost]:
    """Return a powered-up player on ghost `eaten`'s tile and a distant
    ghost.
    """
    player = Player(1, 1, 16, Config(points_per_ghost=33))
    eaten = Ghost(1, 1, 16, player, start_time, random.Random(1))
    distant = Ghost(5, 5, 16, player, start_time, random.Random(2))
    player.activate_power_up(start_time)
    eaten.frighten(start_time, reverse=False)
    distant.frighten(start_time, reverse=False)
    return player, eaten, distant


class FreezeCollisionFrameTests(unittest.TestCase):
    """Evaluator Freeze stops timers but keeps collisions live."""

    def test_frozen_frames_keep_frightened_ghost_edible(self) -> None:
        """A long freeze cannot expire the power-up before the collision."""
        evaluator = EvaluatorMode(enabled=True)
        player, eaten, distant = _powered_player_and_ghosts(0)
        evaluator.toggle_freeze(1000)

        for real_time in range(1000, 10_000, 1000):
            player.update_timers(evaluator.game_time(real_time))
        collision_time = evaluator.game_time(10_000)
        resolve_collisions(player, {}, {}, [eaten, distant], collision_time)
        resolve_collisions(player, {}, {}, [eaten, distant], collision_time)
        player.update_timers(collision_time)

        self.assertEqual(collision_time, 1000)
        self.assertEqual(player.score, 33)
        self.assertEqual(eaten.state, GhostState.DEAD)
        self.assertTrue(player.is_powered_up)

    def test_unfreeze_resumes_frightened_time_without_jump(self) -> None:
        """Surviving frightened ghosts keep their remaining time after
        unfreeze.
        """
        evaluator = EvaluatorMode(enabled=True)
        player, eaten, distant = _powered_player_and_ghosts(0)
        evaluator.toggle_freeze(1000)
        resolve_collisions(
            player, {}, {}, [eaten, distant], evaluator.game_time(10_000))
        evaluator.toggle_freeze(10_000)

        distant._manage_state_timers(evaluator.game_time(13_000))
        self.assertEqual(distant.state, GhostState.FRIGHTENED)

        distant._manage_state_timers(evaluator.game_time(14_100))
        self.assertEqual(distant.state, GhostState.CHASE)

    def test_death_while_frozen_costs_one_life_and_respawns_immediately(
        self,
    ) -> None:
        """Freeze remains useful after a lethal collision without
        unfreezing.
        """
        evaluator = EvaluatorMode(enabled=True)
        player = Player(1, 1, 16, Config(lives=2))
        ghost = Ghost(1, 1, 16, player, 0, random.Random(1))
        evaluator.toggle_freeze(1000)

        game_time = evaluator.game_time(20_000)
        resolve_collisions(player, {}, {}, [ghost], game_time)
        evaluator.resolve_frozen_death(player, game_time)

        self.assertEqual(player.lives, 1)
        self.assertTrue(player.is_alive)
        self.assertTrue(player.is_invincible)
        self.assertFalse(player.is_dying)
        self.assertTrue(evaluator.frozen)


class PauseCollisionFrameTests(unittest.TestCase):
    """Esc Pause on a collision frame resolves it at the pre-pause time."""

    def test_collision_after_pause_uses_pre_pause_time(self) -> None:
        """Time spent in the pause menu cannot expire the power-up."""
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)
        player, eaten, distant = _powered_player_and_ghosts(
            clock.get_ticks_ms())

        now.value = 4.9
        clock.pause()
        now.value = 100.0
        clock.resume()
        collision_time = clock.get_ticks_ms()
        resolve_collisions(player, {}, {}, [eaten, distant], collision_time)
        player.update_timers(collision_time)
        distant._manage_state_timers(collision_time)

        self.assertEqual(collision_time, 4900)
        self.assertEqual(player.score, 33)
        self.assertEqual(eaten.state, GhostState.DEAD)
        self.assertTrue(player.is_powered_up)
        self.assertEqual(distant.state, GhostState.FRIGHTENED)


if __name__ == "__main__":
    unittest.main()
