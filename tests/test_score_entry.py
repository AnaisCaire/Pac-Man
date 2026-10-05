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


if __name__ == "__main__":
    unittest.main()
