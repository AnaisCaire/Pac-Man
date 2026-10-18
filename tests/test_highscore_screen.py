"""Centered Hall of Fame screen contracts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pygame

from src.scores.model import ScoreEntry
from src.ui.gfx import bitmap_font
from src.ui.screens.sub_screens import HighscoreScreen


class HighscoreScreenTests(unittest.TestCase):
    """The Top 10 reads as one centered classic scoreboard."""

    def test_title_and_score_rows_are_centered(self) -> None:
        screen = HighscoreScreen(800, 900)
        screen.set_scores([
            ScoreEntry("ANA", 1200),
            ScoreEntry("MARIO", 950),
        ])
        surface = pygame.Surface((800, 900))

        with (
            patch(
                "src.ui.screens.sub_screens.bitmap_font.render_text",
                wraps=bitmap_font.render_text,
            ) as render_text,
            patch("src.ui.screens.sub_screens.raster.blit_to_surface") as blit,
        ):
            screen.draw(surface)

        texts = [call.args[0] for call in render_text.call_args_list]
        self.assertEqual(texts[0], "HALL OF FAME")
        self.assertIn("ANA", texts[1])
        self.assertIn("MARIO", texts[2])

        for call in blit.call_args_list[:3]:
            image = call.args[1]
            x, _y = call.args[2]
            self.assertLessEqual(
                abs(2 * x + image.shape[0] - surface.get_width()),
                1,
            )


if __name__ == "__main__":
    unittest.main()
