"""In-game HUD evaluator badge contracts."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pygame

from src.ui.gameplay import draw_legend
from src.ui.gfx import bitmap_font


class HudEvaluatorBadgeTests(unittest.TestCase):
    """Evaluator lines are drawn only when the game passes them."""

    def drawn_texts(self, evaluator_lines: tuple[str, ...]) -> list[str]:
        """Draw the HUD once and return every rendered text."""
        surface = pygame.Surface((800, 900))
        with patch(
            "src.ui.gameplay.hud.bitmap_font.render_text",
            wraps=bitmap_font.render_text,
        ) as render_text:
            draw_legend(
                surface=surface,
                time_left=90,
                score=0,
                lives=3,
                level_num=1,
                is_powered_up=False,
                hud_y_start=800,
                evaluator_lines=evaluator_lines,
            )
        return [call.args[0] for call in render_text.call_args_list]

    def test_no_badge_in_normal_game(self) -> None:
        """Without evaluator lines the HUD is unchanged."""
        texts = self.drawn_texts(())

        self.assertNotIn("EVALUATOR", texts)
        self.assertNotIn("FREEZE", texts)

    def test_badge_freeze_and_selection_are_drawn(self) -> None:
        """Each evaluator line is rendered on the HUD."""
        texts = self.drawn_texts(("EVALUATOR", "FREEZE", "SELECTED BLINKY"))

        self.assertIn("EVALUATOR", texts)
        self.assertIn("FREEZE", texts)
        self.assertIn("SELECTED BLINKY", texts)


if __name__ == "__main__":
    unittest.main()
