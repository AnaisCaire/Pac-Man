"""Evaluator mode freeze-time contracts."""

from __future__ import annotations

import unittest

from src.game_logic.clock import ProjectClock
from src.game_logic.evaluator import EvaluatorMode


class FakeMonotonic:
    """Controllable monotonic source expressed in seconds."""

    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


class EvaluatorFreezeTests(unittest.TestCase):
    """Freeze must stop game time without leaking into a normal game."""

    def test_disabled_mode_ignores_freeze(self) -> None:
        """A normal game never freezes, whatever the input layer sends."""
        evaluator = EvaluatorMode(enabled=False)

        evaluator.toggle_freeze(1000)

        self.assertFalse(evaluator.frozen)
        self.assertEqual(evaluator.game_time(5000), 5000)

    def test_unfrozen_game_time_follows_clock(self) -> None:
        """Without a freeze, domain code sees the project clock unchanged."""
        evaluator = EvaluatorMode(enabled=True)

        self.assertFalse(evaluator.frozen)
        self.assertEqual(evaluator.game_time(0), 0)
        self.assertEqual(evaluator.game_time(1234), 1234)

    def test_freeze_stops_game_time(self) -> None:
        """While frozen, game time stays at the freeze timestamp."""
        evaluator = EvaluatorMode(enabled=True)

        evaluator.toggle_freeze(1000)

        self.assertTrue(evaluator.frozen)
        self.assertEqual(evaluator.game_time(1000), 1000)
        self.assertEqual(evaluator.game_time(5000), 1000)

    def test_unfreeze_resumes_without_time_jump(self) -> None:
        """Unfreezing continues from the frozen timestamp."""
        evaluator = EvaluatorMode(enabled=True)

        evaluator.toggle_freeze(1000)
        evaluator.toggle_freeze(4000)

        self.assertFalse(evaluator.frozen)
        self.assertEqual(evaluator.game_time(4000), 1000)
        self.assertEqual(evaluator.game_time(4500), 1500)

    def test_repeated_freezes_accumulate(self) -> None:
        """Each freeze/unfreeze cycle subtracts only its own duration."""
        evaluator = EvaluatorMode(enabled=True)

        evaluator.toggle_freeze(1000)
        evaluator.toggle_freeze(3000)
        evaluator.toggle_freeze(5000)
        evaluator.toggle_freeze(6000)

        self.assertEqual(evaluator.game_time(6000), 3000)
        self.assertEqual(evaluator.game_time(7000), 4000)

    def test_pause_during_freeze_is_not_counted(self) -> None:
        """Esc Pause time never reaches the evaluator, so nothing is doubled."""
        now = FakeMonotonic()
        clock = ProjectClock(monotonic=now, sleep=lambda _seconds: None)
        evaluator = EvaluatorMode(enabled=True)

        now.value = 1.0
        evaluator.toggle_freeze(clock.get_ticks_ms())
        clock.pause()
        now.value = 11.0
        clock.resume()
        now.value = 13.0
        evaluator.toggle_freeze(clock.get_ticks_ms())

        self.assertEqual(evaluator.game_time(clock.get_ticks_ms()), 1000)
        now.value = 13.5
        self.assertEqual(evaluator.game_time(clock.get_ticks_ms()), 1500)


if __name__ == "__main__":
    unittest.main()
