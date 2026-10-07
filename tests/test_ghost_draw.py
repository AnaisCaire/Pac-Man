"""Directional ghost sprite rendering contracts."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pygame

from src.game_logic.config import Config
from src.game_logic.entities.ghosts import Ghost, GhostState
from src.game_logic.entities.player import Player
from src.ui.gameplay.entities import ghost_draw


class GhostSpriteTests(unittest.TestCase):
    """Every visible ghost state uses the supplied left/right pair."""

    def setUp(self) -> None:
        ghost_draw._GHOST_IMAGES.clear()
        ghost_draw._SCALED_CACHE.clear()

    def test_loads_all_directional_sprite_files(self) -> None:
        image = np.zeros((1, 1, 4), dtype=np.uint8)

        with patch.object(ghost_draw.raster, "load_rgba", return_value=image) as load:
            ghost_draw._load_ghost_images()

        loaded_names = {Path(call.args[0]).name for call in load.call_args_list}
        self.assertEqual(loaded_names, {
            f"{sprite}_ghost_{direction}.png"
            for sprite in ("red", "pink", "cyan", "yellow", "scared")
            for direction in ("left", "right")
        })

    def test_selects_direction_for_every_normal_and_frightened_sprite(self) -> None:
        ghost_draw._GHOST_IMAGES.update({
            f"{sprite}_{direction}": np.zeros((1, 1, 4), dtype=np.uint8)
            for sprite in ("red", "pink", "cyan", "yellow", "scared")
            for direction in ("left", "right")
        })
        player = Player(1, 1, 16, Config())
        ghost = Ghost(2, 1, 16, player, 0)

        for sprite in ("red", "pink", "cyan", "yellow"):
            ghost.sprite = sprite
            ghost.state = GhostState.CHASE
            ghost.current_direction = (1, 0)
            self.assertEqual(ghost_draw._pick_image_key(ghost), f"{sprite}_right")
            ghost.current_direction = (-1, 0)
            self.assertEqual(ghost_draw._pick_image_key(ghost), f"{sprite}_left")

        ghost.state = GhostState.FRIGHTENED
        ghost.current_direction = (1, 0)
        self.assertEqual(ghost_draw._pick_image_key(ghost), "scared_right")
        ghost.current_direction = (0, 1)
        self.assertEqual(ghost_draw._pick_image_key(ghost), "scared_left")

    def test_draw_insets_ghost_two_pixels_inside_its_tile(self) -> None:
        player = Player(1, 1, 16, Config())
        ghost = Ghost(2, 3, 16, player, 0)
        surface = pygame.Surface((100, 100))
        image = np.zeros((12, 12, 4), dtype=np.uint8)

        with (
            patch.object(ghost_draw, "_load_ghost_images"),
            patch.object(ghost_draw, "_pick_image_key", return_value="red_left"),
            patch.object(ghost_draw, "_scaled_image", return_value=image) as scale,
            patch.object(ghost_draw.raster, "blit_to_surface") as blit,
        ):
            ghost_draw.draw_ghosts(surface, [ghost], 16, 5, 7)

        scale.assert_called_once_with("red_left", 12)
        blit.assert_called_once_with(
            surface,
            image,
            (5 + 2 * 16 + 2, 7 + 3 * 16 + 2),
        )


if __name__ == "__main__":
    unittest.main()
