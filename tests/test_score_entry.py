"""Score-entry screen input contracts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pygame

from src.ui.screens.score_entry import ScoreEntryScreen
from src.ui.gfx import bitmap_font


class ScoreEntryScreenTests(unittest.TestCase):
    """The UI collects a bounded valid name without doing filesystem I/O."""

    def make_screen(self) -> ScoreEntryScreen:
        with patch(
            "src.ui.screens.score_entry.raster.load_rgba",
            return_value=np.zeros((1, 1, 4), dtype=np.uint8),
        ):
            screen = ScoreEntryScreen(800, 900, "game_over.png")
        screen.set_score(123)
        return screen

    def test_typing_backspace_and_submit_create_a_score_entry(self) -> None:
        screen = self.make_screen()
        for character in "Ana 42":
            screen.handle_event(pygame.event.Event(
                pygame.KEYDOWN, key=pygame.K_a, unicode=character
            ))
        screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode=""
        ))

        action = screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""
        ))

        self.assertEqual(action, "submit")
        self.assertEqual(screen.score_entry().name, "Ana 4")
        self.assertEqual(screen.score_entry().score, 123)

    def test_empty_name_shows_validation_error(self) -> None:
        screen = self.make_screen()

        action = screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""
        ))

        self.assertIsNone(action)
        self.assertIsNotNone(screen.error)

    def test_empty_field_draws_a_supported_visible_cursor(self) -> None:
        screen = self.make_screen()
        surface = pygame.Surface((800, 900))

        with patch("src.ui.screens.score_entry._draw_center") as draw_center:
            screen.draw(surface)

        self.assertIn(
            "NAME: I",
            [call.args[1] for call in draw_center.call_args_list],
        )
        self.assertTrue(bitmap_font.render_text("I", 4, (255, 255, 255))[:, :, 3].any())


class EvaluatorRunScoreEntryTests(unittest.TestCase):
    """Evaluator runs are never offered to the highscore board."""

    def make_screen(self) -> ScoreEntryScreen:
        with patch(
            "src.ui.screens.score_entry.raster.load_rgba",
            return_value=np.zeros((1, 1, 4), dtype=np.uint8),
        ):
            screen = ScoreEntryScreen(800, 900, "game_over.png")
        screen.set_score(123, evaluator_run=True)
        return screen

    def test_enter_returns_to_menu_without_a_name(self) -> None:
        """Enter leaves the screen with no name and no validation error."""
        screen = self.make_screen()

        action = screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""
        ))

        self.assertEqual(action, "menu")
        self.assertIsNone(screen.error)

    def test_typing_is_ignored_and_never_submits(self) -> None:
        """No name is collected, so no ScoreEntry can be submitted."""
        screen = self.make_screen()
        actions = [
            screen.handle_event(pygame.event.Event(
                pygame.KEYDOWN, key=pygame.K_a, unicode=character
            ))
            for character in "Ana"
        ]
        actions.append(screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""
        )))

        self.assertEqual(screen.name, "")
        self.assertNotIn("submit", actions)

    def test_draw_says_the_score_is_not_saved(self) -> None:
        """The reviewer sees why no name is requested."""
        screen = self.make_screen()
        surface = pygame.Surface((800, 900))

        with patch("src.ui.screens.score_entry._draw_center") as draw_center:
            screen.draw(surface)

        drawn = [call.args[1] for call in draw_center.call_args_list]
        self.assertIn("EVALUATOR RUN", drawn)
        self.assertIn("SCORE NOT SAVED", drawn)
        self.assertIn("PRESS ENTER FOR MENU", drawn)
        self.assertNotIn("INSERT NAME", drawn)

    def test_normal_set_score_restores_name_entry(self) -> None:
        """A later normal game asks for a name and submits again."""
        screen = self.make_screen()
        screen.set_score(456)
        screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_a, unicode="A"
        ))

        action = screen.handle_event(pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""
        ))

        self.assertEqual(action, "submit")
        self.assertEqual(screen.score_entry().score, 456)


if __name__ == "__main__":
    unittest.main()
