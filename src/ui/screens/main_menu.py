import pygame
from .bottons import UIElement
from ..gfx import raster

import pathlib
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"

BUTTON_FONT_SIZE = 40
LOGO_MAX_WIDTH = 600
BG_COLOR = (106, 159, 181)


class MainMenu:
    """Draws the main menu and returns an action string when a button is clicked."""

    # maps button text / action string for game engine
    ACTIONS = {
        "Start Game":      "play",
        "View Highscores": "highscores",
        "Instructions":    "instructions",
        "Exit":            "quit",
    }

    def __init__(self, screen_width: int, screen_height: int):

        # load / scale  logo to fit
        raw_logo = raster.load_rgba(str(_IMAGES_DIR / "main_screen_logo.png"))
        logo_scale = min(LOGO_MAX_WIDTH / raw_logo.shape[0], 1.0)
        logo_w = int(raw_logo.shape[0] * logo_scale)
        logo_h = int(raw_logo.shape[1] * logo_scale)
        self.logo = raster.nearest_neighbor_scale(raw_logo, logo_w, logo_h)
        self.logo_rect = pygame.Rect((0, 0), (logo_w, logo_h))
        self.logo_rect.center = (screen_width // 2, logo_h // 2 + 20)

        # create UIElement for buttons, evenly spaced below the logo
        cx = screen_width // 2
        top = self.logo_rect.bottom + 40
        spacing = BUTTON_FONT_SIZE + 30
        self.buttons = []
        for i, (label, action) in enumerate(self.ACTIONS.items()):
            btn = UIElement(center_position=(cx, top + i * spacing),
                            text=label,
                            font_size=BUTTON_FONT_SIZE,
                            action=action
                            )
            self.buttons.append(btn)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Call once per event. Returns an action string on click, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    return button.action
        return None

    def update(self, mouse_pos: tuple[int, int]) -> None:
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        raster.blit_to_surface(surface, self.logo, self.logo_rect.topleft)
        for button in self.buttons:
            button.draw(surface)
