import pygame
from .bottons import UIElement
from ..gfx import raster

import pathlib
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"

BUTTON_FONT_SIZE = 40
BG_COLOR = (106, 159, 181)


class VictoryScreen():
    """Victory screen shown when all pac-gums are eaten."""

    def __init__(self, screen_width: int, screen_height: int):
        cx = screen_width // 2
        by = screen_height - 50
        self.back_btn = UIElement(center_position=(cx, by),
                                  text="Return to Main Menu",
                                  font_size=BUTTON_FONT_SIZE,
                                  action="main menu")
        raw_image = raster.load_rgba(str(_IMAGES_DIR / "victory_screen.png"))
        max_h = by - 20
        scale = min(screen_width / raw_image.shape[0],
                    max_h / raw_image.shape[1])
        img_w = int(raw_image.shape[0] * scale)
        img_h = int(raw_image.shape[1] * scale)
        self.image = raster.nearest_neighbor_scale(raw_image, img_w, img_h)
        self.image_rect = pygame.Rect((0, 0), (img_w, img_h))
        self.image_rect.center = (cx, img_h // 2 + 10)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.rect.collidepoint(event.pos):
                return self.back_btn.action
        return None

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.back_btn.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        raster.blit_to_surface(surface, self.image, self.image_rect.topleft)
        self.back_btn.draw(surface)
