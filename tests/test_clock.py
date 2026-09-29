"""Deterministic simulation-clock contracts."""

from __future__ import annotations

import unittest

from src.game_logic.clock import ProjectClock
from src.game_logic.config import Config
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.player import Player


class FakeMonotonic:
    """Controllable monotonic source expressed in seconds."""

    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


class ProjectClockTests(unittest.TestCase):
    """Pause must freeze simulation time without freezing UI frame pacing."""

    def test_pause_freezes_simulation_and_resume_has_no_jump(self) -> None:
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)

        now.value = 1.25
        self.assertEqual(clock.get_ticks_ms(), 1250)
        clock.pause()
        now.value = 99.0
        self.assertEqual(clock.get_ticks_ms(), 1250)
        clock.resume()
        self.assertEqual(clock.get_ticks_ms(), 1250)
        now.value = 99.5

        self.assertEqual(clock.get_ticks_ms(), 1750)

    def test_pause_and_resume_are_idempotent(self) -> None:
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)

        clock.pause()
        clock.pause()
        now.value = 5.0
        clock.resume()
        clock.resume()
        now.value = 6.0

        self.assertEqual(clock.get_ticks_ms(), 1000)

    def test_paused_simulation_does_not_expire_power_or_ghost_timers(self) -> None:
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)
        player = Player(1, 1, 16, Config())
        ghost = Ghost(1, 1, 16, player, 0)
        player.activate_power_up(clock.get_ticks_ms())
        ghost.frighten(clock.get_ticks_ms())

        now.value = 4.0
        player.update_timers(clock.get_ticks_ms())
        ghost._manage_state_timers(clock.get_ticks_ms())
        clock.pause()
        now.value = 100.0
        player.update_timers(clock.get_ticks_ms())
        ghost._manage_state_timers(clock.get_ticks_ms())

        self.assertTrue(player.is_powered_up)
        self.assertEqual(ghost.state, GhostState.FRIGHTENED)

        clock.resume()
        now.value = 101.1
        player.update_timers(clock.get_ticks_ms())
        ghost._manage_state_timers(clock.get_ticks_ms())

        self.assertFalse(player.is_powered_up)
        self.assertEqual(ghost.state, GhostState.CHASE)

    def test_paused_simulation_does_not_advance_respawn_delay(self) -> None:
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)
        player = Player(1, 1, 16, Config(lives=2))
        player.is_alive = False
        player.death_time = clock.get_ticks_ms()

        clock.pause()
        now.value = 100.0
        player.update_timers(clock.get_ticks_ms())

        self.assertFalse(player.is_alive)

        clock.resume()
        now.value = 103.0
        player.update_timers(clock.get_ticks_ms())

        self.assertTrue(player.is_alive)
        self.assertTrue(player.is_invincible)


if __name__ == "__main__":
    unittest.main()
