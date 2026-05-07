import pygame
import pathlib
from ....game_logic.entities.ghosts import Ghost

# entities/ → gameplay/ → ui/ → images/
_IMAGES_DIR = pathlib.Path(__file__).parent.parent.parent / "images"

# keyed by sprite name → loaded Surface (populated on first draw call)
_GHOST_IMAGES: dict[str, pygame.Surface] = {}


def _load_ghost_images() -> None:
    """Load all ghost images from disk once after pygame.init()."""
    if _GHOST_IMAGES:
        return
    # directional variants for Blinky (red)
    _GHOST_IMAGES['red_right'] = pygame.image.load(
        str(_IMAGES_DIR / "ghost_red" / "red_ghost.png")).convert_alpha()
    _GHOST_IMAGES['red_left'] = pygame.image.load(
        str(_IMAGES_DIR / "ghost_red" / "red_ghost_left.png")).convert_alpha()
    # single image per other ghost type
    _GHOST_IMAGES['pink'] = pygame.image.load(
        str(_IMAGES_DIR / "pink_ghost.png")).convert_alpha()
    _GHOST_IMAGES['cyan'] = pygame.image.load(
        str(_IMAGES_DIR / "cyan_ghost.png")).convert_alpha()
    _GHOST_IMAGES['yellow'] = pygame.image.load(
        str(_IMAGES_DIR / "yellow_ghost.png")).convert_alpha()
    # shared scared image for all ghosts when frightened
    _GHOST_IMAGES['scared'] = pygame.image.load(
        str(_IMAGES_DIR / "scared.png")).convert_alpha()


def _pick_image(ghost: Ghost) -> pygame.Surface:
    """Return the correct raw surface for this ghost's current state."""
    if ghost.is_frightened:
        return _GHOST_IMAGES['scared']
    if ghost.sprite == 'red':
        # Blinky has a left/right variant
        key = 'red_right' if ghost.current_direction == (1, 0) else 'red_left'
        return _GHOST_IMAGES[key]
    # all other sprites are single images
    return _GHOST_IMAGES.get(ghost.sprite, _GHOST_IMAGES['red_right'])


def draw_ghosts(surface: pygame.Surface, ghosts: list[Ghost], tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """Draw all ghosts using their sprite and state."""
    _load_ghost_images()

    for ghost in ghosts:
        if ghost.is_dead:
            continue  # invisible while returning home

        raw = _pick_image(ghost)
        image = pygame.transform.scale(raw, (tile_size, tile_size))

        px = offset_x + (ghost.grid_x + ghost.progress * ghost.current_direction[0]) * tile_size
        py = offset_y + (ghost.grid_y + ghost.progress * ghost.current_direction[1]) * tile_size
        surface.blit(image, (int(px), int(py)))
