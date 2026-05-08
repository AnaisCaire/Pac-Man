from .bottons import UIElement
import pygame
import pathlib
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"

BUTTON_FONT_SIZE = 40
BG_COLOR = (106, 159, 181)
LOGO_MAX_WIDTH = 600



class HighscoreScreen():
    """
    mario = put content inside
    """

    def __init__(self, screen_width: int, screen_height: int):
        # back button:
        cx = screen_width // 2 # center it
        by = screen_height - 150 # bottom
        self.back_btn = UIElement(center_position=(cx, by),
                             text="Back",
                             font_size=BUTTON_FONT_SIZE,
                             action="back")
    
    def handle_event(self, event: pygame.event.Event) -> str | None:
        """ Use pygame event class to track if mouse on btn"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.rect.collidepoint(event.pos):
                return self.back_btn.action
        return None
    
    def update(self, mouse_pos: tuple) -> None:
        """ update the mouse position"""
        self.back_btn.update(mouse_pos)
    
    def draw(self, surface: pygame.Surface) -> None:
        """ add together """
        surface.fill(BG_COLOR)
        self.back_btn.draw(surface)


class InstructionsScreen():
    """
    give instructions
    """
    def __init__(self, screen_width: int, screen_height: int):
        # back button:
        cx = screen_width // 2 # center it
        by = screen_height - 50 # bottom
        self.back_btn = UIElement(center_position=(cx, by),
                             text="Back",
                             font_size=BUTTON_FONT_SIZE,
                             action="back")
        # scale the image
        raw_image = pygame.image.load(str(_IMAGES_DIR / "instructions.png")).convert_alpha()
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


class PauseScreen():
    """Full-screen pause menu with Resume and Return to Main Menu buttons."""

    ACTIONS = {
        "Resume":            "resume",
        "Return to Menu":    "menu",
    }

    def __init__(self, screen_width: int, screen_height: int):

         # load / scale  logo to fit
        raw_logo = pygame.image.load(str(_IMAGES_DIR / "main_screen_logo.png")).convert_alpha()
        logo_scale = min(LOGO_MAX_WIDTH / raw_logo.get_width(), 1.0)
        logo_w = int(raw_logo.get_width() * logo_scale)
        logo_h = int(raw_logo.get_height() * logo_scale)
        self.logo = pygame.transform.scale(raw_logo, (logo_w, logo_h))
        self.logo_rect = self.logo.get_rect(center=(screen_width // 2, logo_h // 2 + 20))

        cx = screen_width // 2
        cy = screen_height // 2
        spacing = BUTTON_FONT_SIZE + 30
        self.buttons = []
        for i, (label, action) in enumerate(self.ACTIONS.items()):
            offset = (i - (len(self.ACTIONS) - 1) / 2) * spacing
            btn = UIElement(center_position=(cx, int(cy + offset)),
                            text=label,
                            font_size=BUTTON_FONT_SIZE,
                            action=action)
            self.buttons.append(btn)

    def handle_event(self, event: pygame.event.Event) -> str | None:
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