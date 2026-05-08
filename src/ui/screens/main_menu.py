import pygame
from .bottons import UIElement

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
        raw_logo = pygame.image.load(str(_IMAGES_DIR / "main_screen_logo.png")).convert_alpha()
        logo_scale = min(LOGO_MAX_WIDTH / raw_logo.get_width(), 1.0)
        logo_w = int(raw_logo.get_width() * logo_scale)
        logo_h = int(raw_logo.get_height() * logo_scale)
        self.logo = pygame.transform.scale(raw_logo, (logo_w, logo_h))
        self.logo_rect = self.logo.get_rect(center=(screen_width // 2, logo_h // 2 + 20))

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

    def update(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        surface.blit(self.logo, self.logo_rect)
        for button in self.buttons:
            button.draw(surface)