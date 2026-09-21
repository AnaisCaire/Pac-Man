import pathlib

import numpy as np
import pygame

from ....game_logic.entities.ghosts import Ghost
from ...gfx import raster

# entities/ → gameplay/ → ui/ → images/
_IMAGES_DIR = pathlib.Path(__file__).parent.parent.parent / "images"

# keyed by sprite name → raw RGBA array (populated on first draw call)
_GHOST_IMAGES: dict[str, np.ndarray] = {}
# keyed by (sprite name, tile_size) → nearest-neighbor scaled RGBA array,
# rebuilt only when the tile size changes (e.g. on level load), not per frame
_SCALED_CACHE: dict[tuple[str, int], np.ndarray] = {}


def _load_ghost_images() -> None:
    """Load all ghost images from disk once, on first use."""
    if _GHOST_IMAGES:
        return
    # directional variants for Blinky (red)
    _GHOST_IMAGES['red_right'] = raster.load_rgba(
        str(_IMAGES_DIR / "ghost_red" / "red_ghost.png"))
    _GHOST_IMAGES['red_left'] = raster.load_rgba(
        str(_IMAGES_DIR / "ghost_red" / "red_ghost_left.png"))
    # single image per other ghost type
    _GHOST_IMAGES['pink'] = raster.load_rgba(str(_IMAGES_DIR / "pink_ghost.png"))
    _GHOST_IMAGES['cyan'] = raster.load_rgba(str(_IMAGES_DIR / "cyan_ghost.png"))
    _GHOST_IMAGES['yellow'] = raster.load_rgba(str(_IMAGES_DIR / "yellow_ghost.png"))
    # shared scared image for all ghosts when frightened
    _GHOST_IMAGES['scared'] = raster.load_rgba(str(_IMAGES_DIR / "scared.png"))


def _pick_image_key(ghost: Ghost) -> str:
    """Return the correct raw sprite key for this ghost's current state."""
    if ghost.is_frightened:
        return 'scared'
    if ghost.sprite == 'red':
        # Blinky has a left/right variant
        return 'red_right' if ghost.current_direction == (1, 0) else 'red_left'
    # all other sprites are single images
    return ghost.sprite if ghost.sprite in _GHOST_IMAGES else 'red_right'


def _scaled_image(key: str, tile_size: int) -> np.ndarray:
    cache_key = (key, tile_size)
    scaled = _SCALED_CACHE.get(cache_key)
    if scaled is None:
        scaled = raster.nearest_neighbor_scale(_GHOST_IMAGES[key], tile_size, tile_size)
        _SCALED_CACHE[cache_key] = scaled
    return scaled


def draw_ghosts(surface: pygame.Surface, ghosts: list[Ghost], tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """Draw all ghosts using their sprite and state."""
    _load_ghost_images()

    for ghost in ghosts:
        if ghost.is_dead:
            continue  # invisible while returning home

        image = _scaled_image(_pick_image_key(ghost), tile_size)

        px = offset_x + (ghost.grid_x + ghost.progress *
                         ghost.current_direction[0]) * tile_size
        py = offset_y + (ghost.grid_y + ghost.progress *
                         ghost.current_direction[1]) * tile_size
        raster.blit_to_surface(surface, image, (int(px), int(py)))
