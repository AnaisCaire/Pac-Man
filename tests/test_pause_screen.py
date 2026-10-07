"""Pause-menu exit confirmation contracts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pygame

from src.ui.gfx import bitmap_font
from src.ui.screens.sub_screens import InstructionsScreen, PauseScreen


class PauseScreenTests(unittest.TestCase):
    """Leaving a running session must require one explicit confirmation."""

    def make_screen(self) -> PauseScreen:
        with patch(
            "src.ui.screens.sub_screens.raster.load_rgba",
            return_value=np.zeros((1, 1, 4), dtype=np.uint8),
        ):
            return PauseScreen(800, 900)

    def test_return_to_menu_requires_confirmation(self) -> None:
        screen = self.make_screen()
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))

        with patch(
            "src.ui.screens.sub_screens._handle_button_click",
            return_value="menu",
        ):
            self.assertIsNone(screen.handle_event(event))

        self.assertTrue(screen.confirming_exit)
        self.assertEqual(
            [button.action for button in screen.buttons],
            ["cancel_menu", "confirm_menu"],
        )

        with patch(
            "src.ui.screens.sub_screens._handle_button_click",
            return_value="confirm_menu",
        ):
            self.assertEqual(screen.handle_event(event), "menu")

    def test_exit_confirmation_explains_score_loss(self) -> None:
        """The confirmation states why the player must choose again."""
        screen = self.make_screen()
        screen.confirming_exit = True
        surface = pygame.Surface((800, 900))

        with patch(
            "src.ui.screens.sub_screens.bitmap_font.render_text",
            wraps=bitmap_font.render_text,
        ) as render_text:
            screen.draw(surface)

        self.assertIn(
            "You are going to loose your score",
            [call.args[0] for call in render_text.call_args_list],
        )


class InstructionsScreenTests(unittest.TestCase):
    """Evaluator controls are documented in-game, not hidden."""

    def test_evaluator_controls_are_drawn(self) -> None:
        """Instructions explain how to enable and use evaluator controls."""
        with patch(
            "src.ui.screens.sub_screens.raster.load_rgba",
            return_value=np.zeros((1, 1, 4), dtype=np.uint8),
        ):
            screen = InstructionsScreen(800, 900)
        surface = pygame.Surface((800, 900))

        with patch(
            "src.ui.screens.sub_screens.bitmap_font.render_text",
            wraps=bitmap_font.render_text,
        ) as render_text:
            screen.draw(surface)

        text = " ".join(call.args[0] for call in render_text.call_args_list)
        self.assertIn("EVALUATOR MODE", text)
        self.assertIn("CONFIG", text)
        self.assertIn("F:", text)
        self.assertIn("G:", text)
        self.assertIn("IJKL:", text)
        self.assertIn("C:", text)
        self.assertIn("L:", text)
        self.assertIn("NOT SAVED", text)


if __name__ == "__main__":
    unittest.main()
