"""Evaluator mode freeze-time contracts."""

from __future__ import annotations

import unittest

import pygame

from src.game_logic.clock import ProjectClock
from src.game_logic.config import Config
from src.game_logic.entities.items import Pacgum, SuperPacgum
from src.game_logic.entities.player import Player
from src.game_logic.evaluator import EvaluatorMode
from src.game_logic.game_engine import (
    GameState,
    handle_evaluator_input,
    terminal_state,
)


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


def _level_items() -> tuple[
    dict[tuple[int, int], Pacgum],
    dict[tuple[int, int], SuperPacgum],
]:
    """Return a small uncleared level: two pacgums and one super-pacgum."""
    pacgums = {(1, 1): Pacgum(1, 1, 10), (2, 1): Pacgum(2, 1, 10)}
    super_pacgums = {(3, 1): SuperPacgum(3, 1, 50)}
    return pacgums, super_pacgums


class EvaluatorLevelClearTests(unittest.TestCase):
    """Level clear must end the level through the normal victory path."""

    def test_disabled_mode_does_not_clear_level(self) -> None:
        """A normal game keeps every collectible when L is pressed."""
        evaluator = EvaluatorMode(enabled=False)
        pacgums, super_pacgums = _level_items()

        evaluator.clear_level(pacgums, super_pacgums)

        self.assertEqual(len(pacgums), 2)
        self.assertEqual(len(super_pacgums), 1)

    def test_clear_level_empties_collectibles_in_place(self) -> None:
        """The caller's own dicts are emptied, not replaced."""
        evaluator = EvaluatorMode(enabled=True)
        pacgums, super_pacgums = _level_items()

        evaluator.clear_level(pacgums, super_pacgums)

        self.assertEqual(pacgums, {})
        self.assertEqual(super_pacgums, {})

    def test_cleared_level_is_a_normal_victory(self) -> None:
        """A live player on a cleared level reaches the real VICTORY outcome."""
        evaluator = EvaluatorMode(enabled=True)
        player = Player(1, 1, 16, Config())
        pacgums, super_pacgums = _level_items()

        evaluator.clear_level(pacgums, super_pacgums)

        self.assertIs(
            terminal_state(player, pacgums, super_pacgums),
            GameState.VICTORY,
        )

    def test_clear_level_is_idempotent(self) -> None:
        """Pressing L twice is harmless and still yields one victory."""
        evaluator = EvaluatorMode(enabled=True)
        player = Player(1, 1, 16, Config())
        pacgums, super_pacgums = _level_items()

        evaluator.clear_level(pacgums, super_pacgums)
        evaluator.clear_level(pacgums, super_pacgums)

        self.assertEqual(pacgums, {})
        self.assertEqual(super_pacgums, {})
        self.assertIs(
            terminal_state(player, pacgums, super_pacgums),
            GameState.VICTORY,
        )

    def test_clear_level_waits_for_dying_player(self) -> None:
        """Victory is not declared mid-death; the death resolves first."""
        evaluator = EvaluatorMode(enabled=True)
        player = Player(1, 1, 16, Config())
        pacgums, super_pacgums = _level_items()
        player.start_death_animation()

        evaluator.clear_level(pacgums, super_pacgums)

        self.assertIsNone(terminal_state(player, pacgums, super_pacgums))

    def test_clear_level_does_not_change_score(self) -> None:
        """Cleared collectibles award no points to an evaluator run."""
        evaluator = EvaluatorMode(enabled=True)
        player = Player(1, 1, 16, Config())
        player.score = 120
        pacgums, super_pacgums = _level_items()

        evaluator.clear_level(pacgums, super_pacgums)

        self.assertEqual(player.score, 120)


def _key(key: int) -> pygame.event.Event:
    """Return one KEYDOWN event for `key`."""
    return pygame.event.Event(pygame.KEYDOWN, key=key)


class EvaluatorInputTests(unittest.TestCase):
    """F and L are the only evaluator keys; the adapter owns the mapping."""

    def test_f_toggles_freeze(self) -> None:
        """F freezes on the first press and unfreezes on the second."""
        evaluator = EvaluatorMode(enabled=True)
        pacgums, super_pacgums = _level_items()

        handle_evaluator_input(
            evaluator, [_key(pygame.K_f)], 1000, pacgums, super_pacgums)
        self.assertTrue(evaluator.frozen)
        self.assertEqual(evaluator.game_time(3000), 1000)

        handle_evaluator_input(
            evaluator, [_key(pygame.K_f)], 3000, pacgums, super_pacgums)
        self.assertFalse(evaluator.frozen)
        self.assertEqual(evaluator.game_time(3000), 1000)

    def test_l_clears_level(self) -> None:
        """L empties the level's collectibles."""
        evaluator = EvaluatorMode(enabled=True)
        pacgums, super_pacgums = _level_items()

        handle_evaluator_input(
            evaluator, [_key(pygame.K_l)], 1000, pacgums, super_pacgums)

        self.assertEqual(pacgums, {})
        self.assertEqual(super_pacgums, {})

    def test_disabled_mode_ignores_evaluator_keys(self) -> None:
        """A normal game is unaffected by F and L."""
        evaluator = EvaluatorMode(enabled=False)
        pacgums, super_pacgums = _level_items()

        handle_evaluator_input(
            evaluator,
            [_key(pygame.K_f), _key(pygame.K_l)],
            1000,
            pacgums,
            super_pacgums,
        )

        self.assertFalse(evaluator.frozen)
        self.assertEqual(len(pacgums), 2)
        self.assertEqual(len(super_pacgums), 1)

    def test_other_keys_and_events_are_ignored(self) -> None:
        """Movement keys, Esc and key releases never trigger evaluator aids."""
        evaluator = EvaluatorMode(enabled=True)
        pacgums, super_pacgums = _level_items()

        handle_evaluator_input(
            evaluator,
            [
                _key(pygame.K_UP),
                _key(pygame.K_d),
                _key(pygame.K_ESCAPE),
                pygame.event.Event(pygame.KEYUP, key=pygame.K_f),
                pygame.event.Event(pygame.KEYUP, key=pygame.K_l),
            ],
            1000,
            pacgums,
            super_pacgums,
        )

        self.assertFalse(evaluator.frozen)
        self.assertEqual(len(pacgums), 2)

    def test_two_f_presses_in_one_frame_cancel_out(self) -> None:
        """Each press is one toggle, even when both land in the same frame."""
        evaluator = EvaluatorMode(enabled=True)
        pacgums, super_pacgums = _level_items()

        handle_evaluator_input(
            evaluator,
            [_key(pygame.K_f), _key(pygame.K_f)],
            1000,
            pacgums,
            super_pacgums,
        )

        self.assertFalse(evaluator.frozen)
        self.assertEqual(evaluator.game_time(2000), 2000)


if __name__ == "__main__":
    unittest.main()
