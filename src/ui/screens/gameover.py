import pygame
from .bottons import UIElement

import pathlib
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"

BUTTON_FONT_SIZE = 40
LOGO_MAX_WIDTH = 600
BG_COLOR = (106, 159, 181)

class GameOver():
    """ For the game over screen + add name of player to save score == MARIO """
    def __init__(self, screen_width: int, screen_height: int):
        # return to main menu:
        cx = screen_width // 2 # center it
        by = screen_height - 50 # bottom
        self.back_btn = UIElement(center_position=(cx, by),
                             text="Return to Main Menu",
                             font_size=BUTTON_FONT_SIZE,
                             action="main menu")
        # scale the image
        raw_image = pygame.image.load(str(_IMAGES_DIR / "game_over.png")).convert_alpha()
        max_h = by - 20  # don't overlap the back button
        scale = min(screen_width / raw_image.get_width(), max_h / raw_image.get_height())
        img_w = int(raw_image.get_width() * scale)
        img_h = int(raw_image.get_height() * scale)
        self.image = pygame.transform.scale(raw_image, (img_w, img_h))
        self.image_rect = self.image.get_rect(center=(cx, img_h // 2 + 10))
    
    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.rect.collidepoint(event.pos):
                return self.back_btn.action
        return None

    def update(self, mouse_pos: tuple) -> None:
        self.back_btn.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        surface.blit(self.image, self.image_rect)
        self.back_btn.draw(surface)