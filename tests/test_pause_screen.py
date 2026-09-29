"""Pause-menu exit confirmation contracts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pygame

from src.ui.screens.sub_screens import PauseScreen


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


if __name__ == "__main__":
    unittest.main()
