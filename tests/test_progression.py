"""Headless game-session progression contracts."""

from __future__ import annotations

import unittest

from src.game_logic.config import Config
from src.game_logic.game_engine import (
    GameSession,
    GameState,
    LevelTimer,
    transition_session,
)


class GameSessionTests(unittest.TestCase):
    """Progression keeps only the state the subject says to carry forward."""

    def test_level_completion_keeps_score_and_lives(self) -> None:
        session = GameSession.new(Config(lives=3))
        session.score = 120
        session.lives = 2

        state = transition_session(session, GameState.VICTORY, level_count=10)

        self.assertEqual(state, GameState.IN_GAME)
        self.assertEqual(
            (session.level_index, session.score, session.lives),
            (1, 120, 2),
        )

    def test_final_level_completion_becomes_game_victory(self) -> None:
        session = GameSession(level_index=9, score=120, lives=2)

        state = transition_session(session, GameState.VICTORY, level_count=10)

        self.assertEqual(state, GameState.VICTORY)
        self.assertEqual(
            (session.level_index, session.score, session.lives),
            (9, 120, 2),
        )

    def test_new_session_and_menu_return_reset_progress(self) -> None:
        session = GameSession(level_index=4, score=120, lives=1)

        state = transition_session(session, GameState.MAIN_MENU, level_count=10)
        session.reset(Config(lives=3))

        self.assertEqual(state, GameState.MAIN_MENU)
        self.assertEqual(
            (session.level_index, session.score, session.lives),
            (0, 0, 3),
        )

    def test_timeout_and_defeat_do_not_advance_session(self) -> None:
        session = GameSession(level_index=4, score=120, lives=0)

        state = transition_session(session, GameState.GAME_OVER, level_count=10)

        self.assertEqual(state, GameState.GAME_OVER)
        self.assertEqual(
            (session.level_index, session.score, session.lives),
            (4, 120, 0),
        )

    def test_level_timer_pauses_during_death_until_respawn(self) -> None:
        timer = LevelTimer(start_time=0)

        timer.pause(100)
        self.assertEqual(timer.elapsed_ms(10_000), 100)
        timer.resume(10_000)

        self.assertEqual(timer.elapsed_ms(10_100), 200)


if __name__ == "__main__":
    unittest.main()
